"""
cellulose.cells
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>

This module contains the core functionality of cellulose.

This stuff should be documented pretty well in the docs subdirectory of the
cellulose distribution.

"""

import threading, weakref, warnings

try:
    from threading import local as thread_local
except ImportError:
    warnings.warn("Threading is not supported in python2.3")
    thread_local = object

try:
    set # Only available in Python 2.4+
except NameError:
    from sets import Set as set # Python 2.3 fallback

class CellCallStack(thread_local):
    """
    A stack of DependantCell subclasses that are currently discovering
    dependencies.  (eg, ComputedCell cells push themselves onto the stack while
    their value is being calculated, and when other cells are accessed they
    register themselves as a dependency of the cell on top of the stack.)

    Note that to prevent a dependency from being discovered, push None onto the
    stack while they are being accessed.

    Don't instance this class directly (unless you know what you're doing.)
    Instead, use the global cellulose.dependant_cell_stack.
    """
    def __init__(self):
        self._call_stack = []
        self.call_when_empty = set()
        self.call_when_empty.add(lambda: None)

    def push(self, cell):
        """
        Pushes a cell onto the stack to discover dependencies.

        In general, you'll want to use DependantCell.push() instead.  (It just
        calls this method with itself, but it looks clearer.)

        If you want to access a cell without it being reported as a dependency
        of whatever is on the stack, you can push None.  Just be sure to pop
        it back off when you're done!  (Use a try/finally.)
        """
        if cell is not None:
            assert cell not in self._call_stack  # Circular dependency
        self._call_stack.append(cell)

    def pop(self, cell):
        """
        Pops a cell off the stack.

        (Just as with push, you'll probably want to use DependantCell.pop()
        instead.)

        This method requires that you explicitly state what you expect to pop.
        This is to help catch bugs with cells not being popped when they should,
        causing dependencies to be directed to the wrong dependants.
        """
        popped = self._call_stack.pop()
        if popped != cell:
            # We only want to warn, not raise an exception.  This is because
            # most of the time that this happens, it is due to another problem,
            # which would be overshadowed by an exception being raised here.
            warnings.warn("Popped %r, expected %r" % (popped, cell),
                    stacklevel=2)
            # Clean up the stack... hopefully...
            if cell in self._call_stack:
                while popped != cell:
                    popped = self._call_stack.pop()
        while len(self._call_stack) == 0 and self.call_when_empty:
            self.call_when_empty.pop()()
        return popped

    def _get_current(self):
        if self._call_stack:
            return self._call_stack[-1]
        else:
            return None
    current = property(_get_current)

dependant_cell_stack = CellCallStack()


class DependencyCell(object):
    """
    This class provides the functionality of a cell that can be used as a
    dependency of others.  It is not meant to be instanced, but subclassed.
    """
    def __init__(self):
        self.dependants = {}

    def register_dependant(self, dependant):
        if dependant is None: return
        id_ = id(dependant)
        if not id_ in self.dependants:
            # Note that we call ``unregister_dependant`` instead of removing
            # the the id directly.  This is to make it easier for subclasses
            # to catch dependant removal.
            self.dependants[id_] = weakref.ref(dependant,
                    lambda _: self.unregister_dependant(id_))
        # We call this even if we already have this dependant.  This is so
        # that the dependant can tell when we are no longer a dependency.
        dependant.register_dependency(self)

    def depended(self):
        """
        Called whenever data is retrieved from us, and we need to be made a
        dependency of the cell on the stack.
        """
        if dependant_cell_stack.current is not None:
            self.register_dependant(dependant_cell_stack.current)

    def unregister_dependant(self, dependant):
        """
        Called by a dependant when it no longer wants to be notified of changes.

        This function is also called when a dependant is garbage collected, in
        which case only the id is passed.
        """
        if isinstance(dependant, int):  id_ = dependant
        else:                           id_ = id(dependant)
        del self.dependants[id_]

    def changed(self):
        """
        This function should be called when this cell is known to have changed
        and the depenants need to be notified.

        Note that to be lazy, ``changed`` should only be called when the cell
        is known, without any doubt, to have changed.  If there is only a
        possibility of change, ``possibly_changed`` should be called instead.
        """
        for wr in self.dependants.values():
            wr().dependency_changed()

    def possibly_changed(self):
        """
        This function should be called when this cell *might* have changed.
        """
        for wr in self.dependants.values():
            wr().dependency_possibly_changed(self)

    def verify_changed(self):
        """
        Called when a dependant is verifying if a possibly changed dependency
        has actually changed.

        Returns None, but calls self.changed() if it has changed.

        This method should be implemented by any cell that calls the
        self.possibly_changed() method.

        It is reasonable for an implementation of this method to 'lie'.  For
        example, if calculating the respective value is very expensive, but
        taking a 99% accurate guess at if it has changed is cheap, giving a
        false negative (or positive) should be acceptable.  This is especially
        true if the dependant cell often changes its dependencies.  (Note: None
        of the cell classes included in cellulose lie in this method.)
        """
        raise NotImplementedError


class DependantCell(object):
    """
    A cell that can discover dependencies, (ie inputs,)  and be alerted of
    changes in those dependencies.

    Note that this class does not have an associated value.  (Opposed to a
    ComputedCell.)  This allows for more flexibility in the system.

    This class is not meant to be instanced, but subclassed.
    """
    def __init__(self):
        self.dependencies = {}
        self._possibly_changed_dependencies = {}
        self._dirty = True

        self._deep_dependencies = None

    def deep_dependencies(self):
        """
        Deep dependencies is a way to track dependencies of interest, without
        having to search every cell of the dependency graph.

        This functionality currently isn't used anywhere, although I intend to
        use it for networking.  (For example, I'll want to quickly know if a
        particular cell depends in any way on a cell over a network connection.)
        I imagine it could also have many other application specific uses.

        FIXME:  The current implementation of this feature takes for granted
        that dependencies only change when the resulting value is changed, but
        this is not the case.  It is possible that a change in dependencies
        would result in the same value, thus dependant cells never hear of the
        change.  As such this cannot *currently* be relied upon.  Contact me if
        you are interested in using it.
        """
        if hasattr(self, 'update_dependencies'):
            self.update_dependencies()
        if self._deep_dependencies is None:
            self._deep_dependencies = set()
            for d in self.dependencies.values():
                if hasattr(d, 'deep_dependencies'):
                    self._deep_dependencies.update(d.deep_dependencies)
        return self._deep_dependencies
    deep_dependencies = property(deep_dependencies)

    def register_dependency(self, dependency):
        self.dependencies[id(dependency)] = dependency

    def dependency_changed(self):
        """
        Called by a dependency when it knows for certain that it has changed.

        This method can also be used if, for some reason, the cached value needs
        to be expired manually.
        """
        if self._dirty:
            return
        # We no longer care about possibilities of changed dependencies; we now
        # know that one has definitely changed!
        self._possibly_changed_dependencies = {}
        self._dirty = True
        # Just because a dependency has changed, doesn't actually mean that we
        # have changed.  However, there is that possibility; we need to
        # alert any dependants.
        self.possibly_changed()

    def dependency_possibly_changed(self, dependency):
        """
        Called by a dependency to alert us that it might have changed, (but is
        putting off verifying it.)
        """
        if self._dirty:
            return # If we are already dirty we don't care.
        if not self._possibly_changed_dependencies:
            self.possibly_changed()
        self._possibly_changed_dependencies[id(dependency)] = dependency

    def _verify_possibly_changed_dependencies(self):
        while self._possibly_changed_dependencies:
            id_ = self._possibly_changed_dependencies.keys()[0]
            d = self._possibly_changed_dependencies.pop(id_)
            # Recalculate the dependency
            d.verify_changed()
            # If the dependency actually changed, we will have been set to
            # dirty, and _possibly_changed_dependencies cleared.

    def push(self):
        """
        Begins dependency discovery for this cell.
        """
        dependant_cell_stack.push(self)
    def pop(self):
        """
        Ends dependency discover for this cell.

        Note that this should be called once for every call to push().  Be sure
        to wrap anything that happens in-between in a try/finally block.
        """
        dependant_cell_stack.pop(self)

    def update_dependencies(self):
        """ Makes sure that the list of dependencies is up to date, without
        calling self.depended().  This method is called when the
        deep_dependencies property is accessed.

        I'm not sure if this method will stick around, as I think it is only
        used with the faulty deep dependencies implementation.
        """
        if hasattr(self, 'get'):
            dependant_cell_stack.push(None)
            try:
                self.get()
            finally:
                dependant_cell_stack.pop(None)
        else:
            raise NotImplementedError

# As a side note, I'm beginning to see why CS is so full of confusing
# terminology.  'Dependency' and 'Dependant' are very similar words, but in this
# context have opposite meanings.  (This is especially problematic for someone
# like me; I often say the opposite of what I mean.)  However, I have searched
# backward and forward through a thesaurus and haven't found anything that
# describes the concepts half as well!


class InputCell(DependencyCell, DependantCell):
    """
    InputCell

    A cell that has its value explicitly assigned.
    """
    def __init__(self, value=None, restriction=None):
        DependencyCell.__init__(self)
        # Dependant functionality is only used for restrictions
        DependantCell.__init__(self)

        # We store the originally set value (_set_value) and post-restriction
        # value (_value) separately to prevent the possibility of side effects
        # when retrieving the value between restriction changes.
        # For example, imagine we are using a restriction that is initially a
        # DecimalRangeRestriction with a max of 5.0, and a value of 5.0 is set
        # to the cell.  Somewhere, the max is set down to, say, 1.0, and then
        # later back to 5.0.  If we were not storing both the original and the
        # current value, the following two conditions would arise:
        #     1) The value *was not* accessed while the max was at 1.0, in which
        #        case the value would *remain at 5.0.*
        #     2) The value *was* accessed while the max was at 1.0, which would
        #        have adjusted the value to 1.0.  Later, when the max is
        #        returned to 5.0, the value would *remain at 1.0.*
        # Thus, we store the original, so that the value rebounds back to the
        # original value, regardless as to whether or not it was accessed.

        # ... or I could have avoided this alltogether by not allowing
        # restrictions to modify a value.  But, it only adds two lines and
        # modifies one other, so I don't think it's a problem.  Strange how I
        # used 20 lines of comments to explain it. :P

        # The value as it was explicitly set, before being passed through any
        # restrictions:
        self._set_value = value

        # The value that is ultimately visible:
        self._value = None

        self._restriction = restriction

    def _get_restriction(self):
        return self._restriction
    def _set_restriction(self, restriction):
        self._restriction = restriction
        if restriction:
            self.dependency_changed()
    restriction = property(_get_restriction, _set_restriction)

    def get(self):
        """
        Returns the value that was set, after it has been filtered through the
        restriction.

        In general, I recommend using the 'value' property instead.  To me,
        using 'get' makes me feel like I should be using a dictionary, while
        'value' reminds me that it's a cell.  (Python isn't Java, after all.)
        """
        self._verify_possibly_changed_dependencies()
        if self._dirty:
            self.set(self._set_value)
        self.depended()
        return self._value

    def set(self, value):
        """
        Sets the value for this cell.

        Note that the value is adjusted to the restriction eagerly, rather than
        lazily.  It could be made lazy easy enough, but if the restriction
        raises an exception, it's helpful to have it happen when you assign it,
        not when you read it.  (Restrictions normally don't cost much anyway!)

        As mentioned in the docstring for ``get``, it is recommended to use
        the property ``value`` instead of ``set`` directly.
        """
        self._set_value = value
        old = self._value
        if self.restriction:
            self.push()
            try:
                self._value = self.restriction.adjust(value)
            finally:
                self.pop()
        else:
            self._value = value
        self._dirty = False
        self._deep_dependencies = None
        if value != old:
            self.changed()
    value = property(get, set)

    def verify_changed(self):
        # See comments on verify_changed in DependencyCell and ComputedCell.
        self.get()


class ComputedCell(DependencyCell, DependantCell):
    """
    ComputedCell

    A cell that gets it's value by calling a function.

    While it is not (currently) enforced, it is highly recommended that the
    function used to calculate the value does not have any side-effects.  There
    is no guarantee when the function will be called, if it is called at all.

    If you need to do something in response to a ComputedCell changing, do it
    in a separate cell.  (such as the ones provided in cellulose.observers.)
    """
    def __init__(self, function=None, restriction=None):
        DependencyCell.__init__(self)
        DependantCell.__init__(self)

        self._value = None
        self._function = function
        self._restriction = restriction

    def get(self):
        self._verify_possibly_changed_dependencies()
        if self._dirty:
            self.run()
        self.depended()

        return self._value

    value = property(get) #There is no set, as this should be readonly.

    def _get_restriction(self):
        return self._restriction
    def _set_restriction(self, restriction):
        self._restriction = restriction
        self.dependency_changed()
    restriction = property(_get_restriction, _set_restriction)

    def verify_changed(self):
        # With an implementation like this, this method might seem redundant.
        # This is here for any more specialized subclasses, where calculating
        # the value might be considerably more expensive that determining if it
        # is changed.
        self.get()

    def set_function(self, new):
        old = self._function
        self._function = new
        if new != old:
            self.dependency_changed()
    function = property(lambda self: self._function, set_function)

    def run(self):
        if not self.function:
            raise AttributeError('function is not set!') #FIXME better exception

        old_deps = self.dependencies
        self.dependencies = {}
        old_value = self._value

        self.push()
        try:
            if self.restriction:
                self._value = self.restriction.adjust(self.function())
            else:
                self._value = self.function()
        finally:
            self.pop()

        self._dirty = False
        self._deep_dependencies = None

        ## Remove links from dependencies that are no longer needed
        for id_ in set(old_deps).difference(set(self.dependencies)):
            d = old_deps[id_]
            d.unregister_dependant(self)


        if old_value != self._value:
            self.changed()


