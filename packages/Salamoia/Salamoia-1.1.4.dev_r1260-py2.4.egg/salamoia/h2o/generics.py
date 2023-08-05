from salamoia.h2o.functional import partial, rpartial

__all__ = ['Any', 'GenericFunction']

class GenericFunction(object):
    """
    This object references a method using its name

    When called it searches for an attribute with this name
    and executes it.
    """
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):        
        return getattr(args[0], self.name)(*args[1:], **kwargs)

    def __get__(self, obj, typ):
        """
        When a generic funcion is access through an attribute in an instance or class
        the property protocol invokes this method which returns a "bound" method,
        actually a partial method with the first argument bound to self

        If the object is None this means that the generic is accessed through a class an not an instance
        and simply returns itself.
        
        """
        if obj is None:
            return self
        return partial(self, obj)
    
class AnyMetaclass(type):
    def __getattr__(self, name):
        return GenericFunction(name)    

class Any(object):
    """
    A generic is a wrapper to a method but with late binding:

    >>> class TestGeneric(object):
    ...   def test(self, arg):
    ...     return arg + 1
    >>> class TestGenericChild(TestGeneric):
    ...   def test(self, arg):
    ...     return arg * 2
    
    >>> x = Any.test
    >>> tg, tgc = TestGeneric(), TestGenericChild()
    >>> x(tg, 10)
    11
    >>> x(tgc, 10)
    20

    This is mostly useful if we want to create higher order functions

    >>> from salamoia.h2o.functional import rpartial
    >>> map(rpartial(Any.test, 10), [tg, tgc])
    [11, 20]

    (Remember that the generic function expects 'self' as the first argument)

    Generics are also very useful to generate partial functions to methods
    replacing "compose_methods" and similar property based hacks (TODO: benchmark)

    
    The compose function let's you compose two functions.
    The compose_methods let's you compose two methods.
    But if you want to compose a function with a method?
    The problem is that inside class definitions you get plain functions
    but outside you get unbound methods. (even worst with class methods, that inside class def
    are not even callable)

    
    compose_methods catches each access to the composed method with a propery (__get__) accessor
    and returns a composed method with bound/unbound functions.
    
    Past versions had a special compose_function_method that did the same but only on the second argument.
    With generics this is no more necessary, because compose will invoke __get__ if the callabel is not a plain function:

    >>> from salamoia.h2o.functional import compose
    >>> def base(arg):
    ...   return arg - 1
    >>> class ComposeTest(object):
    ...   def test(self, arg):
    ...     return arg*10
    ...
    ...   ctest = compose(base, Any.test)
    >>> ct=ComposeTest()

    >>> ComposeTest.ctest(ct, 1)
    9
    >>> ct.ctest(1)
    9

    For the same reasons in older versions there was a symmetric "compose_method_function" method.
    With generics it's no more necessary:

    >>> def test(arg):
    ...   return arg * 10
    >>> class ComposeTest(object):
    ...   def base(self, arg):
    ...     return arg - 1
    ...
    ...   ctest = compose(Any.base, test)
    >>> ComposeTest().ctest(1)
    9

    Now let's see if we can replace even the "compose_methods";

    >>> from salamoia.h2o.functional import compose_methods
    >>> class ComposeTest(object):
    ...   def base(self, arg):
    ...     return arg - 1
    ...   def test(self, arg):
    ...     return arg*10
    ...
    ...   ctest = compose_methods(base, test)
    >>> ComposeTest().ctest(1)
    9

    >>> class ComposeTest(object):
    ...   def base(self, arg):
    ...     return arg - 1
    ...   def test(self, arg):
    ...     return arg*10
    ...
    ...   ctest = compose(Any.base, Any.test)
    >>> ComposeTest().ctest(1)
    9

    Wow! It works. The compose_methods function is kept because it may be more efficent. (TODO: bench)

    And class methods? 
    You can (and should) operate on them like with normal function

    >>> class ComposeTest(object):
    ...   @classmethod
    ...   def base(cls, arg):
    ...     return arg - 1
    ...   @classmethod
    ...   def test(cls, arg):
    ...     return arg*10
    ...
    ...   ctest = compose(base, test)
    >>> ComposeTest.ctest(1)
    9

    """

    __metaclass__ = AnyMetaclass

class Multicall(object):
    """
    A multicall is a wrapper around a list of objects that
    allows to simply call a method on each element of the list
    and return a list of results.

    >>> Multicall([' test ', 'rest ']).strip()
    ['test', 'rest']

    You could do the same using map(Any.strip, [...])
    but this way you can easly pass arguments to the method

    >>> Multicall(['package/module', 'p1/p2/module']).replace('/', '.')
    ['package.module', 'p1.p2.module']

    You may notice that you can do the same using generics and partial functions:

    >>> map(rpartial(Any.replace, '/', '.'), ['package/module', 'p1/p2/module'])
    ['package.module', 'p1.p2.module']

    But it's less confortable to write. Notice however that this is in fact the way it is implemented.
    """
    def __init__(self, sequence):
        self._sequence = sequence

    def __getattr__(self, name):
        def call(*args, **kwargs):
            return map(rpartial(getattr(Any, name), *args, **kwargs), self._sequence)
        return call

class HavingAttr(object):
    """
    Use as:

    >>> HavingAttr([1, 'test', None]).__add__
    [1, 'test']

    It's useful mostly in combination with Multicall:

    >>> Multicall(HavingAttr([1, None, ' test']).strip).strip()
    ['test']

    To avoid duplicating the method name you can use the MulticallHavingAttr sugar
    """
    def __init__(self, sequence):
        self._sequence = sequence

    def __getattr__(self, name):
        return filter(rpartial(hasattr, name), self._sequence)

class MulticallHavingAttr(HavingAttr):
    """
    Sytactical sugar for of Multicall(HavingAttr(list).method).method(..)

    >>> MulticallHavingAttr([1, None, ' test']).strip()
    ['test']

    >>> 
    """
    def __getattr__(self, name):
        return getattr(Multicall(super(MulticallHavingAttr, self).__getattr__(name)), name)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
