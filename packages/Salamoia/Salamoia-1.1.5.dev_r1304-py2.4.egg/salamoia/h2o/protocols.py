"""
This module extends the PyProtocols package
"""

# python 2.5 will have absolute/relative imports
# it will be:
# from __future__ import absolute_import
# from protocols import *

from salamoia.h2o.logioni import Ione

import sys
_pyprotocols = __import__('protocols')
sys.modules['_pyprotocols'] = _pyprotocols
from _pyprotocols import *
del sys.modules['_pyprotocols']

from salamoia.h2o.decorators import unimplemented
from salamoia.h2o.delegate import DelegateOn
from salamoia.h2o.functional import partial, rpartial
from operator import is_not


class DelegatingAdapter(DelegateOn.subject, Adapter):
    """
    A delegating adapter forwards methods to the adapted object but invokes them 
    with this object as self
    
    For example:

        >>> class DelegatingTest(DelegatingAdapter):
        ...   def override(self, arg):
        ...     return self.subject.override(arg) * 2
        >>> class Original(object):
        ...   def test(self, arg):
        ...     return self.override(arg)
        ...   def override(self, arg):
        ...     return arg + 4

        >>> Original().test(12)
        16
        >>> DelegatingTest(Original()).test(12)
        32
        
    """

def filterConforming(protocol, sequence):
    """
    This function returns only the values from the sequence that can adapt to the protocol.
    (the returned values are adapted values, not original values)
    
    >>> class ITestX(Interface):
    ...   pass
    >>> declareAdapter(lambda x:100, [ITestX], forTypes=[int])
    >>> filterConforming(ITestX, [1,"test", 1.3])
    [100]

    There is a more OO interface to the filterConforming function:

    >>> class ITestY(Interface):
    ...   pass
    >>> declareAdapter(NO_ADAPTER_NEEDED, [ITestY], forTypes=[int])
    >>> ITestY.conformingItems([1, "test"])
    [1]

    """
    _marker = object()
    # equivalent. Which one is more readable?
    #return [obj for obj in [adapt(ect, protocol, _marker) for ect in sequence] if obj is not _marker]
    return filter(partial(is_not, _marker), map(rpartial(adapt, protocol, _marker), sequence))

Interface.conformingItems = classmethod(filterConforming)

##########

_multiAdapterRepository = {}

def declareMultiAdapter(adapter, provides, forProtocols=(), forTypes=()):
    """
    This is a shortcut to declareMultiAdapterForProtocol and declareMultiAdapterForType

    using forTypes is currently not implemented::

        >>> declareMultiAdapter(None, [None], forTypes=[int])
        Traceback (most recent call last): 
        ...
        NotImplementedError: not implemented

    """
    for protocol in provides:
        for typ in forTypes:
            declareMultiAdapterForType(adapter, protocol, typ)

        for proto in forProtocols:
            declareMultiAdapterForProtocol(adapter, protocol, proto)

@unimplemented
def declareMultiAdapterForType(adapter, provides, types):
    pass

def declareMultiAdapterForProtocol(adapter, provides, protocols):
    """
    Protocol is a tuple of protocols. Provides is a protocol

    This function registers a multi-adapter on the protocols `protocols` adapting the protocols `provides`
    with the adapter `adapter`. See `multiAdapt`
    """
    if not _multiAdapterRepository.has_key(provides):
        _multiAdapterRepository[provides] = []

    plist = _multiAdapterRepository[provides]
    plist.append((protocols, adapter))

    # a little bit lowlevel in PyProtocols
    directlyImplied = [x[0] for x in provides.getImpliedProtocols() if x[1][0] is NO_ADAPTER_NEEDED]

    # setup alias multi-adapter maps for directly implied adapters
    # this allows to interchangeably use protocols declared as 'equivalentProtocols'
    for d in directlyImplied:
        _multiAdapterRepository[d] = plist
    
    

_marker = object()
def multiAdapt(objects, protocol, default=_marker, debug=False):
    """
    This is a very simple implementation of multi adaptation. 
    It offers an interface similar to PyProtocols single adapters. 

    NOTE: This implementation is not complete, it doesn't rank adapters offering the more specific combination but
    it returns the first matching adapter in declaration order.

    Multi adaptation is used like normal adaptation. The difference is that you adapt a tuple of objects to a protocol.
    When you declare a multi-adapter with `declareMultiAdapter` using a tuple of protocols for `forProtocols`,
    you will adapt each tuple of objects for which every object adapts to each corresponding protocol.

    The resulting tuple of adapted objects is then applied as arguments to the adapter callable

    >>> class IOne(Interface):
    ...   pass
    >>> class ITwo(Interface):
    ...   pass
    >>> declareAdapter(lambda x: x+1, [IOne], forTypes=[int])
    >>> declareAdapter(lambda x: x+2, [ITwo], forTypes=[int])

    >>> class IMulti(Interface):
    ...   pass
    >>> multiAdapt((0, 1), IMulti, 'test')
    'test'
    
    >>> def factory(one, two):
    ...   return one + two
    >>> declareMultiAdapter(factory, [IMulti], forProtocols=[(IOne, ITwo)])
    >>> multiAdapt((0, 1), IMulti, 'test')
    4
    """
    
    if debug:
        Ione.warning("multiAdapt debug: multi adapting", protocol, _multiAdapterRepository.get(protocol),
                     _multiAdapterRepository)

    for pr, adapter in _multiAdapterRepository.get(protocol) or ():
        if debug:
            Ione.warning("multiAdapt debug: len(objects) (%s) == len(pr) (%s) -> %s",
                         len(objects), len(pr), len(objects) == len(pr))
        if len(objects) == len(pr):
            try:
                if debug:
                    Ione.warning("multiAdapt debug: trying", objects, pr)
                return adapter(*map(lambda x, y: adapt(x, y), objects, pr))
            except AdaptationFailure, err:
                if debug:
                    Ione.error("multiAdapt debug: adaptation failure", err)
                pass                

    if default == _marker:
        raise TypeError, "cannot multi adapt %s to %s" % (objects, protocol)
    return default


from salamoia.h2o.concurrency import ThreadLocalClass

class ContextualInterfaceClass(ThreadLocalClass, InterfaceClass):
    """
    This is the metaclass of ContextualInterface. 

    Contextual interface offers a threadlocal read-only property 'context'.
    """

    @property
    def context(self):
        return self.classThreadLocal.context


class ContextualInterface(object):
    """
    A common problem using interfaces and adapters is that
    sometimes you need to propagate some external information into the adapters
    during the adaptation.

    One solution is to put this data inside the object being adapted. Often that
    is not possible, for example because the objects are immutable or there are 
    reentrancy issues.

    Another solution is to use multi adaptation. However the current multi-adapter 
    implementation in salamoia is quite limited and not optimized for performance.

    This solution is based upon a thread local 'global' variable, that is a variable
    accissible from the global scope (and thus from the adapters) but which mantains
    it's value locally to each thread.

    While this solution can be done 'manually' (using globally visible thread locals)
    here is presented an easier access interface to it.

    >>> from threading import Thread
    >>> class IContextualInterfaceTest(ContextualInterface):
    ...   pass

    >>> def outerTest():
    ...   t = Thread(target=testThread)
    ...   t.start()
    ...   t.join()
    ...   return IContextualInterfaceTest.context * 2

    >>> def testThread():
    ...   IContextualInterfaceTest.duringContext(30, innerTest)

    >>> def innerTest():
    ...   assert IContextualInterfaceTest.context == 30

    >>> IContextualInterfaceTest.duringContext(10, outerTest) 
    20

    TODO: implement in python 2.5 with 'with'

    This is the building block of a semplified API using 'contextualAdapt'.

    ------ implementation tests (move in separate file)

    Now let's test if it's compatible with adapters:

    >>> def contextualTestAdapter(self):
    ...  return self + 1
    >>> declareAdapter(contextualTestAdapter, [IContextualInterfaceTest], forTypes=[int])
    >>> IContextualInterfaceTest(3)
    4

    Let's try with a second interface

    >>> class ISecondContextualInterfaceTest(ContextualInterface):
    ...   pass
    
    >>> def secondContextualTestAdapter(self):
    ...  return self + 2
    >>> declareAdapter(secondContextualTestAdapter, [ISecondContextualInterfaceTest], forTypes=[int])
    >>> ISecondContextualInterfaceTest(3)
    5

    """
    __metaclass__ = ContextualInterfaceClass

    @classmethod
    def duringContext(self, context, callable, *args, **kwargs):
        if not hasattr(self.classThreadLocal, 'context'):
            self.classThreadLocal.context = None

        old = self.classThreadLocal.context

        self.classThreadLocal.context = context
        try:
            return callable(*args, **kwargs)
        finally:
            self.classThreadLocal.context = old

def contextualAdapt(value, protocol, context=_marker, default=_marker):
    """    
    Contextual adapt is a shortcut for invoking IContextualInterface.duringContext

    >>> class IContextualTest(ContextualInterface):
    ...   pass

    >>> def testAdapter(self):
    ...   return IContextualTest.context * self

    >>> declareAdapter(testAdapter, [IContextualTest], forTypes=[int])
    >>> contextualAdapt(3, IContextualTest, 20)
    60
    """
    # with no context the contextual adaptation degrades to normal adaptation
    if context is _marker:
        return adapt(value, protocol)

    if default is _marker:
        return protocol.duringContext(context, adapt, value, protocol)
    else:
        return protocol.duringContext(context, adapt, value, protocol, default=default)

def ContextualAdapter(protocol, default=None):
    """
    This function offers an parametric base class for adapters.
    Adapters inheriting ContextualAdapter(SomeInterface)
    will automatically obtain a 'context' attribute got from SomeInterface.context
    during initialization of the adapter instance.

    It works only with interfaces subclasses of ContextualInterface.

    The following is a useful pattern:

    >>> class IContextualTest(ContextualInterface):
    ...   pass

    >>> class IContextualAdapterTest(ContextualInterface):
    ...   pass

    >>> class ContextualAdapterTest(Adapter):
    ...   advise(instancesProvide=[IContextualAdapterTest], asAdapterForTypes=[int])
    ...   def __init__(self, subject):
    ...     super(ContextualAdapterTest, self).__init__(subject)
    ...     self.context = IContextualAdapterTest.context
    ...   def test(self):
    ...     return self.context * self.subject

    >>> contextualAdapt(2, IContextualAdapterTest, 10).test()
    20

    The problem is that the protocol will no more be passed as the optional second argument
    to the adapter in new versions of PyProtocols:

    #>>> def oldAdapter(self, proto):
    #...   return proto
    #>>> declareAdapter(oldAdapter, [IContextualTest], forTypes=[str])
    #>>> IContextualTest('test') is IContextualTest
    #True

    However this kind of code is no more permitted, so we need to use some tricks.

    The ContextualAdapter function is used to generate a parametrized ContextualAdapter class.

    >>> class ContextualAdapterTest(ContextualAdapter(IContextualTest, ",")):
    ...   advise(instancesProvide=[IContextualTest], asAdapterForTypes=[str])
    ...   def test(self, arg):
    ...     return self.context.join([self.subject, arg])

    >>> contextualAdapt("one", IContextualTest, ", ").test("two")
    'one, two'

    >>> adapt("one", IContextualTest).test("two")
    'one,two'

    """
    class ContextualAdapter(Adapter):
        def __init__(self, subject):
            Adapter.__init__(self, subject)
            self.context = protocol.context
            if self.context is None:
                self.context = default

    return ContextualAdapter

def DelegatingContextualAdapter(protocol):
    """
    Metaclass conflict in python must be handled manually
    """
    class DelegatingContextualAdapter(DelegateOn.subject, ContextualAdapter(protocol)):
        pass

    return DelegatingContextualAdapter
