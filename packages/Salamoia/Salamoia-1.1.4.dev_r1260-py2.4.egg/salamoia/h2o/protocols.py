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
    
    >>> class ITest(Interface):
    ...   pass
    >>> declareAdapter(lambda x:100, [ITest], forTypes=[int])
    >>> filterConforming(ITest, [1,"test", 1.3])
    [100]

    There is a more OO interface to the filterConforming function:

    >>> class ITest(Interface):
    ...   pass
    >>> declareAdapter(NO_ADAPTER_NEEDED, [ITest], forTypes=[int])
    >>> ITest.conformingItems([1, "test"])
    [1]

    """
    _marker = object()
    # equivalent. Which one is more readable?
    #return [obj for obj in [adapt(ect, protocol, _marker) for ect in sequence] if obj is not _marker]
    #return filter(partial(is_not, _marker), map(rpartial(adapt, protocol, _marker), sequence))
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
