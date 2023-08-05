__all__ = ["defineVariable"]

import sys

def defineVariable(arg):
    """
    This decorator is useful because allows to associate a docstring to a variable,
    mostly for doctest purposes.

    >>> @defineVariable
    ... def test():
    ...   '''some doc'''
    ...   return 10
    
    Then test becomes a normal variable

    >>> test
    10
    >>> test = 30
    >>> test
    30
    
    The doc is saved in a function object called __docvar_<varname> in the global namespace of the calling function.
    If you use __all__ to limit public module visibility' don't forget to add __docvar_<varname> for each variable
    you want to be available to pydoc (and similars)

    >>> __docvar_test.__doc__
    'some doc'

    The doctests are useful especially when the variable is indeed an higher order function, and deserves
    documentation and testing.

    Now let's define some doctest:

    >>> @defineVariable
    ... def test():
    ...   '''
    ...   some doc
    ...   >>> 1
    ...   1
    ...   '''
    ...   return 10

    
    >>> from doctest import DocTestFinder, DocTestRunner
    >>> tests = DocTestFinder().find(__docvar_test)
    >>> len(tests)
    1
    >>> runner = DocTestRunner()
    >>> runner.run(tests[0])
    (0, 1)

    TODO: don't pollute global namespace unless global testing mode is enabled
    or the caller is from module __main__ (same rules as for salamoia.testing)
    """

    globals = sys._getframe(1).f_globals
    globals["__docvar_"+arg.func_name] = arg
    return arg()

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
