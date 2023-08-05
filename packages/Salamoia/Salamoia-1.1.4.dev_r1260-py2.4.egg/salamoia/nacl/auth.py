#from salamoia.h2o.user import User
from salamoia.h2o.logioni import Ione
import time

from protocols import Interface, protocolForURI, Attribute, advise

class IAuthentication(Interface):
    """
    The authentication interface defines what is the bare minimum interface for an object
    which is used as the authentication 'user'
    """
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/IAuthentication')])

    id = Attribute("The object ID")
    

class AuthToken(object):
    """
    An auth token caches user/password 
    """

    timeout = 60*20

    def __init__(self, principal):
        self.principal = principal

        # temporary compat
        self.user = principal.username
        self.password = principal.password

        self.stamp = time.time()

    def key(self):
        """
        returns the user associated with the token
        """
        return self.user

    def isExpired(self):
        now = time.time()
        return (now - self.stamp) > self.timeout

    def timeRemaining(self):
        now = time.time()
        return self.timeout - (now - self.stamp) 

class AuthTokenCache(object):
    """
    Collects AuthToken objects an provide a way
    to quickly search and check them

    Tokens are maintained in a list an in a dictionary
    hashed by name.
    """
    def __init__(self):
        self._tokens = []
        self._byName = {}

    def add(self, token):
        """
        Add a token to the cache.
        """
        self._tokens.append(token)
        if self._byName.has_key(token.key()):
            raise "token already present"
        self._byName[token.key()] = token

    def remove(self, token):
        """
        Remove a token from the cache.
        """
        self._tokens.remove(token)
        del self._byName[token.key()]

    def invalidate(self):
        """
        Remove all token caches
        """
        self._byName.clear()
        self._tokens = []

    def byName(self, name):
        """
        Returns the token matching 'name'
        """        
        tok = self._byName.get(name)
        if tok and tok.isExpired():
            self.expireToken(tok)
            return None
        return tok

    def checkCredentials(self, principal):
        """
        quickly tests if the password matches
        the corresponding cached token
        """
        tok = self.byName(principal.username)
        if tok:
            if tok.principal.password == principal.password:
                return True
    
    def expireToken(self, token):
        Ione.log("expiring auth token", token.user)
        self.remove(token)

    def names(self):
        return [t.user for t in [self.byName(x.user) for x in self.tokens()] if t]

    def tokens(self):
        return self._tokens

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
