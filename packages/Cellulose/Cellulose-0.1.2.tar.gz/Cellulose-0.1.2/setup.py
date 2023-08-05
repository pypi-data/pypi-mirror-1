from setuptools import setup, find_packages
setup(
    name = "Cellulose",
    version = "0.1.2",
    packages = find_packages(),

    author = "Matthew Marshall",
    author_email = "matthew@matthewmarshall.org",
    description = "Stateful, object-oriented, pseudo-functional programming in python.",
    license = "BSD",
    keywords = "cellulose dependency discovery lazy evaluation caching",
    long_description = """
Cellulose provides a mechanism for maintaining consistency between
inter-dependant values with caching and lazy evaluation.

You can think of it like a spreadsheet program --  Many cells are are calculated
from the values of other cells.  When one cell changes, all of the dependant
cells get updated with new values.

However, cellulose goes quite a ways beyond this.  It guarantees that when a
value is read, it is consistant with all the values it depends on.  It also is
lazy (read: efficient.)  Calculating a value is put off till the very last
possible moment, and only recalculated when absolutely needed.

Dependency discovery and cache invalidation are fully transparent and automatic.
This greatly reduces a major source of bugs in software.

A goal of the project is to be as simple as possible, (but no simpler,) so that
anyone wanting to seriously use it could easily understand the internals.

Cellulose is similar in purpose to PyCells, but is in a way 'lower level'.  It
tries real hard to stay out of your way, but, as a result, lacks some of the
helpers that PyCells provides.  The most essential algorithmic difference is
probably that Cellulose desperatly wants to be lazy, while in PyCells everything
is calculated immediately (by default.)  (On the flipside of this, observers in
PyCells are quite a bit easier to work with.)
    """,
    zip_safe = True,
)