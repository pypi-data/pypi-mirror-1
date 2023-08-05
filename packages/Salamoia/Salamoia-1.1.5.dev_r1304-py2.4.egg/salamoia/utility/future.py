from Queue import Queue, Empty
from threading import Thread
import sys

from salamoia.h2o.delegate import DelegateOn
from salamoia.h2o.decorators import lazy

class Channel(Queue):
    """
    A channel is a queue augmented with useful methods.

    Basic communication channel:

    >>> from threading import Thread
    >>> c = Channel()
    >>> acc = 0

    >>> def producer():
    ...   c.put(1)
    ...   c.put(2)
    ...   c.put(3)

    >>> def consumer():
    ...   global acc
    ...   for i in xrange(0, 3):
    ...     acc = acc + c.get()

    >>> t1 = Thread(target=producer)
    >>> t2 = Thread(target=consumer)
    >>> t1.start()
    >>> t2.start()

    >>> acc
    6

    >>> x = c.get_future()
    >>> type(x) is Future
    True
    

    >>> class TestObject(object):
    ...   def __init__(self, value):
    ...     self.value = value
    ...   def test(self, arg):
    ...     return arg + self.value

    >>> c.put(TestObject(1))

    >>> x.test(2)
    3

    """
    def get_future(self, block=False):
        try:
            return self.get_nowait()
        except Empty:
            return Future(self)

    _real_get = Queue.get

class FutureChannel(Channel):
    def get(self, block=False):
        return self.get_future(block)

class FutureException(object):
    def __init__(self, exc_info):
        self.exc_info = exc_info

class Future(DelegateOn._present):
    def __init__(self, channel):
        self._channel = channel

    @lazy
    def _present(self):
        res = self._channel._real_get()
        if isinstance(res, FutureException):
            raise res.exc_info[0], res.exc_info[1], res.exc_info[2]
        return res

    def __repr__(self):
        return self._present.__repr__()

    def __str__(self):
        return self._present.__str__()

def future(func):
    """
    Decorator marks callables that are executed immediately in a new thread
    and return a future proxy

    >>> import time

    >>> @future
    ... def test(arg):
    ...   time.sleep(1)
    ...   return arg + 1

    >>> r = test(1)
    >>> type(r) is Future
    True
    >>> r
    2

    Exceptions should be propagated on the first access to the future object:

    >>> @future
    ... def test(arg):
    ...   time.sleep(1)
    ...   return 0/0

    >>> r = test(1)
    >>> type(r) is Future
    True
    >>> r
    Traceback (most recent call last):
    ...
        return 0/0
    ZeroDivisionError: integer division or modulo by zero
    """

    def f(*args, **kwargs):

        channel = Channel()

        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except:
                res = FutureException(sys.exc_info())                    

            channel.put(res)
        
        t = Thread(target=wrapper, args=args, kwargs=kwargs)
        t.start()
        
        return channel.get_future()

    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    
    return f

def present(obj):
    """
    Unwraps the future object, eventually waiting until future becomes present.
    """
    return obj._present
