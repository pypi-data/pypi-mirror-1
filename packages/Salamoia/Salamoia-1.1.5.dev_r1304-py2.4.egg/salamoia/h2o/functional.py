"""
From python cook book
"""

__all__ = ['partial', 'rpartial', 'compose', 'mcompose','compose_methods',
           'negp', '__docvar_negp']

import operator

# credits: Peter Harris <scav at blueyonder.co.uk> (partially modified)
class partial(object):
    """
    Partial function callable.
    
    Takes a callable and an argument list.
    When called appends the arguments to the initial arguments.
    Useful for higher order functions.
    """
    def __init__(*args, **kw):
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)

    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)

    def __get__(self, obj, typ):
        """
        This method is an addition to the python cook book receipe.

        It allows partial function to be applied to method and classmethods

        >>> class PartialTest(object):
        ...   def test(self, arg):
        ...     return arg*10
        ...
        ...   ptest = partial(test, 10)
        >>> PartialTest().ptest()
        100
        """
        return partial(self.fn.__get__(obj, typ), *self.args, **self.kw)

def partialProperty(getter):
    """
    This decorator provides a simple way of creating a setter and a getter with few lines
    of code, in the case that the getter function already exists or can be expressed with a simple expression lambda

    >>> class TestPartialProperty(object):
    ...   @partialProperty(lambda self: self._value)
    ...   def value(self, val):
    ...     self._value = val * 10
    >>> p = TestPartialProperty()
    >>> p.value = 10
    >>> p.value
    100
    """
    return partial(property, getter)

class AttributeAccessor(object):
    """
    This function is a quick and convenient way to create a function that
    returns the value of one object's attribute.

    It can be used in two ways.

    >>> class Test(object):
    ...   pass
    >>> test = Test()
    >>> test.value = 10

    The first way is to use attribute names as strings::

    >>> AttributeAccessor('value')(test)
    10

    The second is to specify the desired attribute name directly using attribute access (magic will do the rest)::

    >>> AttributeAccessor.value(test)
    10
    
    This simple object is very useful for example when you are declaring adapters that
    return components contained in attributes of the adapted object, or in many other situations
    when you can save your eyes from a ugly lambda::

    >>> x = Test()
    >>> x.nest = test
    >>> compose(AttributeAccessor.value, AttributeAccessor.nest)(x)
    10

    Or better:
    >>> AttributeAccessor.nest.value(x)
    10

    TODO: it would be nice if automatic composition occours when doing AttributeAccessor.nest.value (??? done?)
    """

    class __metaclass__(type):
        def __getattr__(self, name):
            return _accessorWrapper(rpartial(getattr, name))
        def __call__(self, name):
            return _accessorWrapper(rpartial(getattr, name))

class _accessorWrapper(object):
    """
    This helper class for AttributeAccessor. It allows composition of nested attributes
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getattr__(self, name):
        return _accessorWrapper(compose(AttributeAccessor(name).func, self.func))


class rpartial(partial):
    """
    Reversed partial. Like partial but prebound arguments are "right-aligned"
    (in other words, variable parameters are inserted *before* bound parameters)
    """
    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(args + self.args), **d)
    
def declareAdapterDecorator(*args, **kwargs):
    """
    Short way of defining an adapter

    >>> from protocols import protocolForURI
    >>> ITestInterface = protocolForURI("salamoia.h2o.functional.declareAdapterDecorator.ITestInterface")
    >>> @declareAdapterDecorator([ITestInterface], forTypes=[basestring])
    ... def myadapter(self):
    ...   return self.upper()

    >>> ITestInterface('hello')
    'HELLO'
    """

    from protocols import declareAdapter
    return rpartial(declareAdapter, *args, **kwargs)

# credits: Scott David Daniels
class compose(object):
    """
    compose functions. compose(f,g,x...)(y...) = f(g(y...),x...))

    >>> def a(x, y):
    ...   return x + y
    >>> def b(x, y):
    ...   return x * y    

    >>> x = mcompose(a, b, 10) # TODO: mcompose -> compose
    >>> x(4, 8)
    42
    >>> a(b(4, 8), 10)
    42
    """
    def __init__(self, f, g, *args, **kwargs):
        self.f = f
        self.g = g
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        return self.f(self.g(*args, **kwargs), *self.pending, **self.kwargs)

    def __get__(self, obj, typ):
        """
        Binds the callable unless it is a plain function
        """
        types = __import__('types')
        f = self.f
        g = self.g
        if not isinstance(f, types.FunctionType):
            f = f.__get__(obj, typ)
        if not isinstance(g, types.FunctionType):
            g = g.__get__(obj, typ)

        return compose(f, g, *self.pending, **self.kwargs)



class compose_methods(compose):
    def __get__(self, obj, typ):
        """
        This allows to compose two methods

        >>> class ComposeTest(object):
        ...   def base(self, arg):
        ...     return arg - 1
        ...   def test(self, arg):
        ...     return arg*10
        ...
        ...   ctest = compose_methods(base, test)
        >>> ComposeTest().ctest(1)
        9

        The other way to do this is to use 'Any'. See generics
        This function will be probably obsoleted if the generics module proves to work well
        """
        return compose(self.f.__get__(obj, typ), 
                       self.g.__get__(obj, typ), 
                       *self.pending, **self.kwargs)

# credits: Scott David Daniels
class mcompose(compose):
    """
    compose functions. mcompose(f,g,x...)(y...) = f(*g(y...),x...))

    >>> def a(x, y):
    ...   return x + y
    >>> def b(x, y):
    ...   return x*10, y*10

    >>> x = mcompose(a, b)
    >>> x(4, 8)
    120
    >>> a(*b(4, 8))
    120
    """

    TupleType = type(())

    def __init__(self, f, g, *args, **kwargs):
        self.f = f
        self.g = g
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        mid = self.g(*args, **kwargs)
	if isinstance(mid, self.TupleType):
            return self.f(*(mid + self.pending), **self.kwargs)
        return self.f(mid, *self.pending, **self.kwargs)        

from salamoia.h2o.decorators import defineVariable

@defineVariable
def negp():
    """
    This is what is really fascinating me from functional programming

    >>> def somePredicate(obj):
    ...   return obj > 10
    >>> notSomePredicate = negp(somePredicate)
    
    >>> somePredicate(4)
    False
    >>> notSomePredicate(4)
    True
    """    
    return partial(compose, operator.not_)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
