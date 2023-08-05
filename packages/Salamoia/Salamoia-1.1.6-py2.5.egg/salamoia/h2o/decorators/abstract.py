"""
"""

def abstract(func):
    """
    This decorator help quickly document abstract methods:

    example::

        >>> class A(object):
        ...   @abstract
        ...   def test(self):
        ...     "method docstring...."

        >>> A().test()
        Traceback (most recent call last): 
        ...
        NotImplementedError: should be overriden
      
    """

    def override(*args, **kwargs):
        raise NotImplementedError, "should be overriden"
    override.__name__ = func.__name__
    return override

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
