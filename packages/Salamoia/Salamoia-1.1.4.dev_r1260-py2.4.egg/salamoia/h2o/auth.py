from protocols import Interface, advise, protocolForURI, declareAdapter

__all__ = ['IPrincipal', 'Principal']

class IPrincipal(Interface):
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/IPrincipal')])

class Principal(object):
    advise(instancesProvide=[IPrincipal])

    def __init__(self, username, password=None, service=None):
        self.username = username
        self.password = password
        self.service = service

IAttributeStorable = protocolForURI('http://interfaces.salamoia.org/IAttributeStorable')

declareAdapter(lambda x: x.username, [IAttributeStorable], forProtocols=[IPrincipal])

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
