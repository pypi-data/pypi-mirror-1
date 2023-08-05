"""
cellulose.celltypes
Copyright 2006 by Matthew Marshall <matthew@matthewmarshall.org>


This module contains some cellulose enabled mutable data types.

"""


from cellulose.cells import DependencyCell, ComputedCell, dependant_cell_stack
from cellulose.descriptors import ComputedCellDescriptor, InputCellDescriptor

class CellMeta(type):
    """ Metaclass for simplifying making a cell-friendly subclass.  (It's
    really an oversimplification in most cases.)

    Check out CellSet to see an example.
    """
    depend_methods = [] # methods that trigger dependant_cell_stack.add_dependency
    change_methods = [] # methods that trigger self.changed()
    def __init__(cls, name, bases, dct):
        super(CellMeta, cls).__init__(name, bases, dct)

        def create_depend(name):
            def method(self, *args, **kwargs):
                self.depended()
                return getattr(super(cls, self), name)(*args, **kwargs)
            return method
        def create_changed(name):
            def method(self, *args, **kwargs):
                res = getattr(super(cls, self), name)(*args, **kwargs)
                self.changed()
                return res
            return method

        for names, create in ((cls.depend_methods, create_depend),
                              (cls.change_methods, create_changed)):
            for name in names:
                new = create(name)
                old = getattr(cls, name)
                new.__name__ = old.__name__
                new.__doc__ = old.__doc__
                setattr(cls, name, new)


class CellList(DependencyCell, list):
    """ list subclass that plays well with cells.
    FIXME Optimally, this should behave smarter.  (ie, if only one of the items
    are accessed, we should only alert if that one changes.)
    """
    __metaclass__ = CellMeta
    depend_methods = ['__add__', '__contains__', '__eq__', '__ge__',
        '__getitem__', '__getslice__', '__gt__', '__hash__', '__iadd__',
        '__imul__', '__iter__', '__le__', '__lt__', '__mul__',
        '__ne__', '__repr__', '__reversed__', '__rmul__', '__str__', 'count',
        'index',]
    change_methods = ['__delattr__', '__delitem__', '__delslice__',
        '__setitem__', '__setslice__', 'append', 'extend', 'insert', 'pop',
        'remove', 'reverse', 'sort']

    def __init__(self, sequence=tuple()):
        DependencyCell.__init__(self)
        list.__init__(self, sequence)

    @ComputedCellDescriptor
    def _length(self):
        # We need to manually make ourselves a dependency of this ComputedCell.
        self.depended()
        return list.__len__(self)

    def __len__(self):
        return self._length


class CellSet(DependencyCell, set):
    __metaclass__ = CellMeta
    depend_methods = ['copy', 'difference', 'intersection', 'issubset',
        'issuperset', 'symmetric_difference', 'union', '__and__', '__cmp__',
        '__contains__', '__eq__', '__ge__', '__gt__', '__hash__', '__iand__',
        '__ior__', '__isub__', '__iter__', '__ixor__', '__le__', '__len__',
        '__lt__', '__ne__', '__or__', '__rand__', '__repr__', '__ror__',
        '__rsub__', '__rxor__', '__str__', '__sub__', '__xor__']
    # TODO everything but pop and remove can be made more intelligent.
    change_methods = ['add', 'clear', 'difference_update', 'discard', 'pop',
        'remove', 'symmetric_difference_update', 'update']

    def __init__(self, sequence=tuple()):
        DependencyCell.__init__(self)
        set.__init__(self, sequence)


class _KeyCell(DependencyCell):
    """
    This is a simple helper class for use in CellDict.

    Basically, it allows for Dependants to depend on only one key, instead of
    the entire dict.

    Note that this DOES make CellDict a little heavy.  It might be useful to
    also have a LightCellDict that is a thinner wrapper around dict (using
    only one DependencyCell instance.)
    """
    __slots__ = ('empty_callback', 'dependants')
    def __init__(self, empty_callback=lambda:None):
        DependencyCell.__init__(self)
        # Called when there are no more dependants:
        self.empty_callback = empty_callback
    def unregister_dependant(self, dependant):
        DependencyCell.unregister_dependant(self, dependant)
        if not self.dependants:
            self.empty_callback()

class CellDict(DependencyCell, dict):
    __metaclass__ = CellMeta
    depend_methods = ['__cmp__', '__eq__', '__ge__', '__gt__', '__iter__',
        '__le__', '__len__', '__lt__', '__ne__', '__repr__', '__str__', 'copy',
        'items', 'iteritems', 'iterkeys', 'itervalues', 'keys', 'values']
    change_methods = []

    def __init__(self, *args, **kwargs):
        DependencyCell.__init__(self)

        # A dictionary of subcells.
        self._key_subcells = {}
        dict.__init__(self, *args, **kwargs)

    def _key_changed(self, key):
        if key in self._key_subcells:
            self._key_subcells[key].changed()

    def _key_accessed(self, key):
        if dependant_cell_stack.current is not None:
            if not key in self._key_subcells:
                self._key_subcells[key] = _KeyCell(
                    lambda: self._key_subcells.__delitem__(key))
                # XXX By having a reference to ``self`` in the lambda function,
                # we might be held in memory a lot longer than needed.  I don't
                # know if this is a problem worth fixing.
            self._key_subcells[key].depended()

    def _non_cell_getitem(self, key):
        """ This method is just a small shortcut """
        dependant_cell_stack.push(None)
        try:
            v = self[key]
        finally:
            dependant_cell_stack.pop(None)
        return v

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()
        self._key_changed(key)

    def __setitem__(self, key, v):
        try:
            original_value = self._non_cell_getitem(key)
            missing = False
        except KeyError:
            missing = True
        dict.__setitem__(self, key, v)
        if missing or original_value != self._non_cell_getitem(key):
            self.changed()
            self._key_changed(key)

    def pop(self, key, *args):
        v = dict.pop(self, key, *args)
        self.changed()
        self._key_changed(key)
        return v

    def popitem(self, key, *args):
        v = dict.popitem(self, key, *args)
        self.changed()
        self._key_changed(key)
        return v

    def setdefault(self, key, default):
        self.push()
        try:
            has_key = self.has_key(key)
        finally:
            self.pop()
        if has_key:
            dict.setdefault(self, key, default)
            self.changed()
            self._key_changed(key)

    def clear(self):
        dependant_cell_stack.push(None)
        try:
            keys = set(self.keys())
        finally:
            dependant_cell_stack.pop(None)
        dict.clear(self)
        self.changed()
        for key in keys.intersection(set(self._key_subcells)):
            self._key_changed(key)

    def update(self, *args, **kwargs):
        dependant_cell_stack.push(None)
        try:
            passed_keys = set(kwargs)
            if args:
                passed_keys.update(set(args[0]))

            keys = set(self._key_subcells).intersection(passed_keys)
            originals = {}
            missing = set()
            for key in keys:
                if self.has_key(key):
                    originals[key] = self[key]
                else:
                    missing.add(key)
        finally:
            dependant_cell_stack.pop(None)
        dict.update(self, *args, **kwargs)
        self.changed()
        # Find all of those that were originaly here and have changed.
        dependant_cell_stack.push(None)
        try:
            changed = set()
            for key, v in originals.items():
                if v != self[key]:
                    changed.add(key)
        finally:
            dependant_cell_stack.pop(None)

        for key in changed | missing:
            self._key_changed(key)

    def __getitem__(self, key):
        self._key_accessed(key)
        return dict.__getitem__(self, key)

    def __contains__(self, key):
        # Small issue:  If a cell only accesses the key here, it doesn't need to
        # know when the value has changed, only if the key comes or goes.  I
        # don't know if this is worth fixing or not.
        self._key_accessed(key)
        return dict.__contains__(self, key)

    def get(self, key, default):
        self._key_accessed(self, key)
        return dict.get(self, key, default)

    def has_key(self, key):
        # ditto the comment from __contains__
        self._key_accessed(key)
        return dict.has_key(self, key)


class _ComputedKeyCell(ComputedCell):
    #__slots__ = ('empty_callback', )
    def __init__(self, function, empty_callback=lambda:None):
        ComputedCell.__init__(self, function)
        # Called when there are no more dependants:
        self.empty_callback = empty_callback
    def unregister_dependant(self, dependant):
        ComputedCell.unregister_dependant(self, dependant)
        if not self.dependants:
            self.empty_callback()



class ComputedDict(object):
    """
    A  class with a dictionary-like interface, where values come from calling a
    function with the key as an argument.  (All cellulose enabled, naturally.)
    """

    def __init__(self, function, valid_keys=None, discard_cache=True):
        """
        ComputedDict(function, valid_keys=None, discard_cache=True)

        ``function`` is a function that will be called to get a value for a key.
        This works just like in ``ComputedCell``, only the function is passed
        the key as an argument.

        ``valid_keys`` is a list/set of keys that are valid.  (duh)  If given,
        attempting to access a key not in the list will raise an error.
        Dictionary like methods such as ``has_key``, ``items``, ``keys``, and
        iteneration are also made available.

        Be aware that the value passed here is used directly, not a copy.  This
        means that if you pass it a [Cell]list, then later modify the list, the
        modifications will apply for the ComputedDict instance.

        If ``discard_cache`` is True, a cached value for a key will be discarded
        when it is no longer being depended on. It will be recalculated if it is
        accessed again.  If False, the cached value will live as long as the
        ComputedDict.

        (All three arguments are either properties or InputCellDescriptors of
        the same names, so you are free to change them later.)
        """
        self._key_subcells = {}

        self.function = function
        self.valid_keys = valid_keys
        self.discard_cache = discard_cache

    function = InputCellDescriptor()
    valid_keys = InputCellDescriptor()

    _discard_cache = InputCellDescriptor()
    def _get_discard_cache(self):
        return self._discard_cache
    def _set_discard_cache(self, discard_cache):
        if discard_cache:
            for cell in tuple(self._key_subcells.values()):
                if not cell.dependants:
                    cell.empty_callback()
        self._discard_cache = discard_cache
    discard_cache = property(_get_discard_cache, _set_discard_cache)


    def __getitem__(self, key):
        # TODO move this into the _ComputedKeyCell
        if self.valid_keys and not key in self.valid_keys:
            raise KeyError
        if not key in self._key_subcells:
            def delete():
                if self.discard_cache: del self._key_subcells[key]
            self._key_subcells[key] = _ComputedKeyCell(
                    (lambda: self.function(key)), delete)
        return self._key_subcells[key].value

    def get(self, key, default=None):
        # TODO Maybe this should work even without valid_keys?
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set") # FIXME better exception
        if self.has_key(key):
            return self[key]
        else:
            return default

    def has_key(self, key):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return key in self.valid_keys

    def __contains__(self, key):
        return self.has_key(key)

    def __len__(self):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return len(self.valid_keys)

    def keys(self):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return list(self.valid_keys)

    def values(self):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return [self[k] for k in self.valid_keys]

    def items(self):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return [(k, self[k]) for k in self.valid_keys]

    def __iter__(self):
        if self.valid_keys is None:
            raise AttributeError("valid_keys is not set")
        return iter(self.valid_keys)


