# this decorator caches the result value until of a function the argument funcion of the decorator changes value
# the tester function gets the same arguments the decorated funcion gets
def func_onchange(metric):
    def _inner_onchange(func):
        "A decorator that runs a function only when a generic metric changes."
        def decorated(*args, **kwargs):
            try:
                mresult = metric(*args, **kwargs)
                if decorated._last_metric != mresult:
                    decorated._last_metric = mresult
                    decorated._last_result = func(*args, **kwargs)
            except AttributeError:
                decorated._last_metric = mresult    
                decorated._last_result = func(*args, **kwargs)

            return decorated._last_result
        return decorated
    return _inner_onchange
    
# this decorator caches the result value of a method until the argument funcion of the decorator changes value
# the tester function gets the same arguments the decorated method gets
def method_onchange(metric):
    def _inner_onchange(method):
        "A decorator that runs a method only when a generic metric changes."
        met_name = "_%s_last_metric" % id(method)
        res_name = "_%s_last_result" % id(method)
        def decorated(self, *args, **kwargs):
            try:
                mresult = metric(*args, **kwargs)
                if getattr(decorated, met_name)  != mresult:
                    setattr(decorated, met_name, mresult)
                    setattr(decorated, res_name, method(self, *args, **kwargs))
            except AttributeError:
                setattr(decorated, met_name, mresult)
                setattr(decorated, res_name, method(self, *args, **kwargs))

            return getattr(decorated, res_name)
        return decorated
    return _inner_onchange

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
