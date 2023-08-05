"""
"""

def unimplemented(func):
    """
    This decorator help quickly document unimplemented methods:

    example::
    
    >>> class A(object):
    ...   @unimplemented
    ...   def test(self):
    ...     "method docstring...."

    >>> A().test()
    Traceback (most recent call last): 
    ...
    NotImplementedError: not implemented
      
    """

    def override(*args, **kwargs):
        raise NotImplementedError, "not implemented"
    override.__name__ = func.__name__
    return override

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
