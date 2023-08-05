__all__ = ['Delegate', 'DelegateOn', 'DelegatedObject']

from salamoia.h2o.logioni import Ione
from salamoia.h2o.functional import partial

def Delegate(delegateName):
    """
    Delegation is another form of intheritance.
    This function creates a class to be used as a base class.
    This base class will forward invocations to methods that are not defined in this class
    to an object object contained.

    Usually you specify the name of the delegate attribute indirectly calling DelegateOn.someName,
    this will translate to Delegate('someName')

    >>> class DelegationTest(DelegateOn.first, DelegateOn.second):
    ...   def __init__(self, first, second):
    ...     self.first = first
    ...     self.second = second
    ...   def override(self, arg):
    ...     return arg * 2
    >>> class First(object):
    ...   def __init__(self):
    ...     self.value = [1, 2, 3]
    ...   def test(self, arg):
    ...     return self.override(arg)
    ...   def override(self, arg):
    ...     return arg + 4
    >>> class Second(object):
    ...   def test(self, arg):
    ...     return arg - 1
    ...   def override(self, arg):
    ...     return arg + 10
    ...   def onlyInSecond(self, arg):
    ...     return self.test(arg) * 3
    
    
    >>> f = First()
    >>> f.test(10)
    14
    >>> s = Second()
    >>> s.test(10)
    9
    >>> d = DelegationTest(f, s)
    >>> d.first is f
    True
    >>> d.value
    [1, 2, 3]
    >>> d.test(10)
    20
    
    If the attribute is not found in the first delegate it will search in other delegates (in mro order)
    For example in this case Second.onlyInSecond will invoce First.test which will invoke DelegationTest.override
    >>> d.onlyInSecond(10)
    60

    If the method can't be found it will gracefully raise the offending exception
    >>> d.doesNotExist
    Traceback (most recent call last):
    ...
    AttributeError: DelegationTest has no attribute doesNotExist


    The situation is complicated by the fact that the class and the instance can have data attributes. 
    In this case the instance attributes have precedence:

    >>> First.someValue = 10
    >>> d.someValue
    10
    >>> f.someValue = 20
    >>> d.someValue
    20
    """

    class DelegateBase(object):
        pass

    myDelegateBase = DelegateBase
    def __getattr__(self, name):
        """
        """
        # FIX FIX all this is too complicated. We can take the im_func also from a bound method
        # all this tricks to lookup first in the class namespace is not needed

        subject = getattr(self, delegateName)

        if hasattr(subject, name) and not hasattr(type(subject), name):
            return getattr(subject, name)

        if hasattr(type(subject), name):
            attr = getattr(type(subject), name)

            if hasattr(attr, "__get__"):
                func = attr.__get__(subject, type(subject)).im_func
            elif hasattr(attr, "im_func"):
                func = attr.im_func
            else:
                # for normal attributes instance has precedence
                if hasattr(subject, name):
                    return getattr(subject, name)
                return attr

            res = partial(func, self)
            res.__delegate = subject
            return res

        sp = super(myDelegateBase, self)
        if hasattr(sp, '__getattr__'):
            return sp.__getattr__(name)
        raise AttributeError, "%s has no attribute %s" % (type(self).__name__, name)

    DelegateBase.__getattr__ = __getattr__

    return DelegateBase

class DelegateOn(object):
    """
    DelegateOn.someName is equivalent to Delegate('someName')
    """
    class __metaclass__(type):
        def __getattr__(self, name):
            return Delegate(name)

import sys
old_super = super
def super(typ, obj):
    """
    TODO: convert using a class, perhaps a subclass of `super` itself
    so that __doc__ and repr is correct. However the difference is only visible trying to repr(super)

    TODO: handle also super(type1, type2)
    """

    frame = sys._getframe(2)
    locals = frame.f_locals

    # TODO: nicer signature check
    if locals.has_key('self') and frame.f_code.co_name == '__call__' and locals['self'].__dict__.has_key('__delegate'):
        return SuperWrapper(old_super(typ, locals['self'].__dict__['__delegate']), obj)
    return old_super(typ, obj)

super.__doc__ = old_super.__doc__

class SuperWrapper(object):
    def __init__(self, sup, delegatee):
        self.__sup = sup
        self.__delegatee = delegatee

    def __getattr__(self, name):
        superAttr = getattr(self.__sup, name)
        if not hasattr(superAttr, 'im_func'):
            return superAttr
        return partial(superAttr.im_func, self.__delegatee)

sys.modules['__builtin__'].super = super


## OBSOLETE
class DelegatedObject(object):
    def __getattr__(self, name):
        Ione.log("DELEGATED", self.delegate, "getattrs", name)
        if name in [x for x in dir(self.delegate) if x[0] != '_']:
            return getattr(self.delegate, name)
        else:
            return super(DelegatedObject, self).__getattr__(name)



# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
