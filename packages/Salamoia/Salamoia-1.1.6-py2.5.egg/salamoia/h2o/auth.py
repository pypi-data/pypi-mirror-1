from protocols import Interface, advise, protocolForURI, declareAdapter
from salamoia.nacl.auth import AuthToken, AuthTokenCache
from salamoia.h2o.decorators import lazy

__all__ = ['IPrincipal', 'Principal']

class IPrincipal(Interface):
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/IPrincipal')])

class IAuthenticatedPrincipal(Interface):
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/IAuthenticatedPrincipal')])

class Principal(object):
    advise(instancesProvide=[IPrincipal])

    def __init__(self, username, password=None, service=None):
        self.username = username
        self.password = password
        self.service = service
        
        self.groups = []

        self.authInfo = {}

    @classmethod
    def fromToken(self, token, service):
        """
        This is not the same token as nacl.auth.AuthToken (that will be obsoleted)
        """
        principal =  service.proxy("/authmanager")._principalForToken(token, service)

        # TEMP HACK: move authtoken in AuthManager, and make ssh tokens expire etc
        # (TODO: during acl rewrite and generalizations)
        authTokens = AuthTokenCache.defaultCache()
        #if not authTokens.byName(principal.username):
        #    authTokens.add(AuthToken(principal))

        return principal


    @lazy
    def system(self):
        return Principal("system", "system")

class AuthenticatedPrincipal(Principal):
    advise(instancesProvide=[IAuthenticatedPrincipal])

IAttributeStorable = protocolForURI('http://interfaces.salamoia.org/IAttributeStorable')

declareAdapter(lambda x: x.username, [IAttributeStorable], forProtocols=[IPrincipal])

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
