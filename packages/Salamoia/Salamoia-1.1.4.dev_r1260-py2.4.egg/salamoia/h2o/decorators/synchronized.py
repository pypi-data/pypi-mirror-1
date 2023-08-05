from threading import *

class synchronized(object):
    def __init__(self, lock):
        self.lock = lock

    def __call__(self, func):
        def _inner_synchronized(*args, **kwargs):
            self.lock.acquire()
            res = func(*args, **kwargs)
            self.lock.release()
            return res
        return _inner_synchronized

def autosynchronized(func):
    return synchronized(Lock())(func)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
