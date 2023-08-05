################################################################################
#
# Decorator @threadmethod(sec), makes decorated method calls to always 
# execute in a separate new thread with a specified timeout, propagating 
# exceptions, as well as a result. 
# Dmitry Dvoinikov <dmitry@targeted.org>
#
# from threadmethod import *
#
# class NetworkedSomething(object):
#     @threadmethod(10.0)
#     def connect(self, host, port):
#         ... this could take long long time ...
#    
# # the following call throws ThreadMethodTimeoutError upon a 10 sec. timeout
# NetworkedSomething().connect("123.45.67.89", 1234). Similarly, 
#
# @threadmethod()
# def foo():
#     ...
#
# makes foo() an async method, which just executes in a new separate thread
# each time, but that thread is not waited for, it's just launched to execute 
# in parallel.
#
################################################################################

__all__ = [ "threadmethod", "ThreadMethodTimeoutError" ]

################################################################################

class ThreadMethodTimeoutError(Exception): pass

################################################################################

from threading import Thread

class ThreadMethodThread(Thread):
    "ThreadMethodThread, daemonic descendant class of threading.Thread which " \
    "simply runs the specified target method with the specified arguments."

    def __init__(self, target, args, kwargs):
        Thread.__init__(self)
        self.setDaemon(True)
        self.target, self.args, self.kwargs = target, args, kwargs
        self.start()

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception, e:
            self.exception = e
        except:
            self.exception = Exception()
        else:
            self.exception = None

################################################################################

def threadmethod(timeout = None):
    "@threadmethod(timeout), decorator function, returns a method wrapper " \
    "which runs the wrapped method in a separate new thread."

    def threadmethod_proxy(method):
    
        if hasattr(method, "__name__"):
            method_name = method.__name__
        else:
            method_name = "unknown"

        def threadmethod_invocation_proxy(*args, **kwargs):
            worker = ThreadMethodThread(method, args, kwargs)
            if timeout is None:
                return
            worker.join(timeout)
            if worker.isAlive():
                raise ThreadMethodTimeoutError("A call to %s() has timed out" 
                                               % method_name)
            elif worker.exception is not None:
                raise worker.exception
            else:
                return worker.result

        threadmethod_invocation_proxy.__name__ = method_name

        return threadmethod_invocation_proxy

    return threadmethod_proxy
