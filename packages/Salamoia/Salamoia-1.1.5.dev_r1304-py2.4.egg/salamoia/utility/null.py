class Null:
    """ 
    Null objects always and reliably "do nothing." 

    >>> null = Null()
    >>> null.test.blabla().something() is null
    True

    """
    
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "Null"
    def __nonzero__(self): return 0
    
    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
