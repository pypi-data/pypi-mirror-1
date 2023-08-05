import threading

class ThreadLocalClass(type):
    """
    >>> from threading import Thread

    >>> class Test(object):
    ...   __metaclass__ = ThreadLocalClass
    
    >>> def threadTest(arg):
    ...   Test.classThreadLocal.test = arg

    >>> Test.classThreadLocal.test = 10
    >>> t = Thread(target=threadTest, args=(20,))
    >>> t.start()
    >>> t.join()

    >>> Test.classThreadLocal.test
    10
    """
    def __init__(cls, name, bases, dict):
        super(ThreadLocalClass, cls).__init__(name, bases, dict)
        cls.classThreadLocal = threading.local()
