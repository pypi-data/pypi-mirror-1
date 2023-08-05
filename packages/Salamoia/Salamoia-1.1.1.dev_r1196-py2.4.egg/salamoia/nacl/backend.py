from salamoia.nacl.auth      import *
from salamoia.h2o.service    import Service
from salamoia.h2o.acl        import *
from salamoia.h2o.exception  import *
from salamoia.h2o.logioni    import *
from salamoia.h2o.container  import *
from salamoia.h2o.object     import *
from salamoia.nacl.partialfetcher import *
from salamoia.nacl.config    import Config

from salamoia.h2o.backend    import Backend

from optparse import OptionParser
from salamoia.h2o.feedcollection import * 

from pkg_resources import Environment
from salamoia.h2o.bundle import Bundle as Bundle

import time
import os

class NACLBackend(Backend):

    name = "nacl"

    configClass = Config

    def installationPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "installationPath", "/usr/local/salamoia/development")

    def scriptPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "scriptsPath", 
                       os.path.join(self.installationPath(), "scripts"))

    def rootPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "rootPath", "")

    def varPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "varPath", "/var/lib/salamoia")
    


from salamoia.nacl.backendmixin import *
from salamoia.nacl.schema    import SchemaDescription
            
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
        Ione.log("Storing Object (id '%s')" % (object.id))
        Ione.log('========================')
        #Ione.log("CHECKING ACCESS for id '%s'" % (
        #    self.authTokens.byName(self._currentUser).object.id), level=LOG_ERR)
        if not object.checkAcl(self.authTokens.byName(self._currentUser).object.id,
                               WriteAction()):
            Ione.log("ACCESS FAILED!!!!!! (%s)" % (
                self.authTokens.byName(self._currentUser).object.id), level=LOG_ERR)
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
        Ione.log("computed id '%s'" % (object.computeID()))

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
    
    def search(self, searchSpec):
        """
        Returns a list of ids matching the searchSpec
        """
        raise NotImplementedError, "must override"

    def roundtrip(self, object):
        """
        returns the same object
        """
        return object

    def defaultPartialObject(self):
        return PartialObject

    def defaultPartialFetcher(self):
        return PartialFetcher

    def checkCredentials(self, user, password, uri=None):
        """
        called to check the credentials of a RPC request.

        It should return true if the user and password are valid.
        """
        raise NotImplementedError, 'must override'

    def authControl(self, action):
        if action == "invalidateCache":
            Ione.log("Invalidating auth token cache on client request")
            self.authTokens.invalidate()
        if action == "getLoggedUsers":
            return self.authTokens.names();
        return 0

    def _authenticate(self, user, password, uri=None):
        """
        This is an interal method.

        Authentication tokens are cached.
        When 'checkCredentials' is called the first time and
        returns true, the matchin user and password are stored
        in an authentication token. The token will be used on
        subsequent connections to quickly validate the name and
        password, without doing a full 'checkCredentials' lookup    
        """
        Service._authenticate(self, user, password, uri)
        # cache
        if self.authTokens.checkCredentials(user, password):
            return True
        # do complicate login here
        if self.checkCredentials(user, password, uri):
            self.authTokens.add(AuthToken(user, password))
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

# not more necessary
#from ldap.ldapbackend import LDAPBackend
#from flat.flatbackend import FLATBackend

#compatibility. deprecated
Backend.registerBackend("ldap", NACLBackend)
Backend.registerBackend("flat", NACLBackend)

def start():
    """
    This is a simple backend starter function. It is meant to be invoked from the setuptools wrapper script
    """
    NACLBackend.prepare()
    backend = NACLBackend.defaultBackend()

    backend.run()
