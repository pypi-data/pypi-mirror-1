from salamoia.nacl.auth      import AuthToken, AuthTokenCache
from salamoia.h2o.service    import Service
from salamoia.h2o.acl        import WriteAction
from salamoia.h2o.exception  import FetchError
from salamoia.h2o.logioni    import Ione
from salamoia.h2o.config     import Config
from salamoia.h2o.decorators import abstract
from salamoia.nacl.partialfetcher import PartialObject, PartialFetcher

from salamoia.h2o.backend    import Backend

import time
import os

class NACLBackend(Backend):

    name = "nacl"

    configClass = Config

    def installationPath(self):
        cfg = Config()
        return cfg.get('general', "installationPath", "/usr/local/salamoia/development")

    def scriptPath(self):
        cfg = Config()
        return cfg.get('general', "scriptsPath", 
                       os.path.join(self.installationPath(), "scripts"))

    def rootPath(self):
        cfg = Config()
        return cfg.get('general', "rootPath", "")

    def varPath(self):
        cfg = Config()
        return cfg.get('general', "varPath", "/var/lib/salamoia")
    
    def configFilenames(self):
        return ['/usr/share/salamoia/nacl/site.conf', '/etc/salamoia/nacl.conf', '~/.naclrc']

from salamoia.nacl.backendmixin import BackendMixin
            
class BackendService(Service):
    """
    This class implements the XMLRPC server methods exported through the
    Backend server.

    Normally they provide some logging and general actions but most of
    the intelligence is in the objects themselves.

    Please add non basic functionality in BackendMixin superclasses
    (see backendmixin.py)
    """
    
    usage = "Backend Function"
    def __init__(self):

        # for now hardcode this here. in future services will be created from the packages 
        # available in bundles found in the environment

        #env = Environment(['/tmp/salamoia/bundles'])
        #egg = env['developerschemabundle'][0]
        #bundle = Bundle(egg)
        #schema = SchemaDescription(bundle.resourceWrapper("hostello/schema.xml"))

        #self.serviceName = schema.name

        super(BackendService, self).__init__()
        self.authTokens = AuthTokenCache()
        self.usage = self.__class__.usage
        self.startupTime = time.time()	
	
    def store(self, object, mode="auto"):
        """
        Storing an object in the repository.

        mode can be 'auto', 'modify', 'create'
        auto mode automatically determines if you need to
        create or modify the object based on the presence of
        the object in the repository
        
        """
        Ione.log('========================')
        Ione.log("Storing Object (id '%s')", object.id)
        Ione.log('========================')

        if not object.checkAcl(self.authTokens.byName(self._currentUser).object.id,
                               WriteAction()):
            Ione.error("ACCESS FAILED!!!!!! (%s)", self.authTokens.byName(self._currentUser).object.id)
            return 0
        
        #Ione.log("Object to be stored:", object)
        #Ione.log('')

        # TODO find better place
        object.junkCheck()
        
        object.store(mode)
        return 0

    def create(self, object):
        return self.store(object, mode="create")

    def modify(self, object):
        return self.store(object, mode="modify")
        
    def templateStore(self, object):
        """
        If the store involves the creation of an object
        a separate 'fetch' and 'store' could need to be done
        atomically (for example allocing uid numbers).

        Since the RPC is asynchronous in respect to many clients
        the simplest synchronization form is this method, which
        combines a templateFetch and a store in a single method.
        """
        Ione.log("Atomic operation")
        #object.templateFetch()
        Ione.log("computed id '%s'", object.computeID())

        try:
            self.fetch(object.computeID())
        except:
            Ione.log("OKOKOK")    
            #object.store()
            return 0
        
        raise "PORCAMADONNA"

    def fetch(self, id, attributes=None):
        """
        calls baseFetch

        if it returns a list, it wraps it inside a Container
        """
        fetcher = self.baseFetch
        if attributes:
            #fetcher = PartialFetcher(self, attributes)
            fetcher = self.defaultPartialFetcher()(self, attributes)

        if isinstance(id, list):
            return [fetcher(x) for x in id]
        return fetcher(id)

    def baseFetch(self, id):
        #Ione.log("Fetching Object")
        raise FetchError, "Cannot find object"

    def _cachedObject(self, id):
        """
        override in mixins
        """
        return None

    def templateFetch(self, object):
        """
        If the object is not already on the repository then
        it creates a new one but with sensible defaults set.

        The user should pass a partially constructed object in which
        some of the attributes are used to infer the defaults in other
        (for example the id from the user name, the homeDirectory from
        the username, the uidNumber from the first free...)

        usally you start with a parent object and create an empty
        child with createChild(childclass), and then fill the required
        attributes.        

        It's the object's responsibility to implement this
        template filling.

        """
        Ione.log("I'm filling")
        return object.tempateFetch()

    def delete(self, object):
        Ione.log("DELETING porcodio")
        object.delete()
        return 0
    
    @abstract
    def search(self, searchSpec):
        """
        Returns a list of ids matching the searchSpec
        """

    def roundtrip(self, object):
        """
        returns the same object
        """
        return object

    def defaultPartialObject(self):
        return PartialObject

    def defaultPartialFetcher(self):
        return PartialFetcher

    @abstract
    def checkCredentials(self, principal, uri=None):
        """
        called to check the credentials of a RPC request.

        It should return true if the user and password are valid.
        """

    def authControl(self, action):
        if action == "invalidateCache":
            Ione.log("Invalidating auth token cache on client request")
            self.authTokens.invalidate()
        if action == "getLoggedUsers":
            return self.authTokens.names();
        return 0

    def _authenticate(self, principal, uri=None):
        """
        This is an interal method.

        Authentication tokens are cached.
        When 'checkCredentials' is called the first time and
        returns true, the matchin user and password are stored
        in an authentication token. The token will be used on
        subsequent connections to quickly validate the name and
        password, without doing a full 'checkCredentials' lookup    
        """
        self._baseAuthenticate(principal, uri)
        # cache
        if self.authTokens.checkCredentials(principal):
            return True
        # do complicate login here
        if self.checkCredentials(principal, uri):
            self.authTokens.add(AuthToken(principal))
            return True
        else:            
            return False

    def systemInfo(self, action):
        if action == "naclUptime":
            now = time.time()
            return now - self.startupTime
        return 0

    def logout(self):
        """
        Logging out removes the authentication token from the cache
        """
        Ione.log("logging out " + self._currentUser);
        self.authTokens.remove(self.authTokens.byName(self._currentUser))
        return 0

    def xkill(self):
        """
        DEPRECATED
        """
        Ione.log("KILLING: checking permissions to kill")
        return self._server.ckill()

class BackendModularService(BackendMixin, BackendService):
    def __init__(self):
        super(BackendModularService, self).__init__()

def start():
    """
    This is a simple backend starter function. It is meant to be invoked from the setuptools wrapper script
    """
    NACLBackend.prepare()
    backend = NACLBackend.defaultBackend()

    backend.run()

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
