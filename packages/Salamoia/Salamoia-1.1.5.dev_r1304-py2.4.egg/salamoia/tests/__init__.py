"""

docTestsTestAll = False

can be changed to true if you want doctests to be automatically executed when importing
otherwise they will be only executed if the module is executed directly with python module.py


"""

__all__ = ['runDocTests', 'docTestsTestAll']

import sys


docTestsTestAll = False

_auto = object()
def runDocTests(verbose=False):
    import doctest

    mod = sys._getframe(1).f_globals['__name__']

    if docTestsTestAll or mod == '__main__':
        if verbose is _auto:
            verbose = not docTestsTestAll or mod == '__main__'

        doctest.testmod(sys.modules[mod], verbose=verbose)
    
