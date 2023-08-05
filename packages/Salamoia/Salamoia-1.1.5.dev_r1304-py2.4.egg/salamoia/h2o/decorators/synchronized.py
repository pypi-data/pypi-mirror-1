from threading import *

class synchronized(object):
    """

    >>> class Test(object):
    ...   def __init__(self, val):
    ...     self.val = val
    ...   @autosynchronized
    ...   def test(self, arg):
    ...     self.val = self.val + arg
    ...     return self.val

    >>> t = Test(4)
    >>> t.test(10)
    14
    >>> t.test(4)
    18

    """
    def __init__(self, lock):
        self.lock = lock

    def __call__(self, func):
        def _inner_synchronized(*args, **kwargs):
            self.lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                self.lock.release()
        return _inner_synchronized

def autosynchronized(func):
    return synchronized(Lock())(func)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
