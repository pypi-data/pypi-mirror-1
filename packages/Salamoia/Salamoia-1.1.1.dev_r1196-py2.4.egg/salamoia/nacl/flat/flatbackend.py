from salamoia.nacl.backend import *
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *
from connection import Connection
#from search import *
from fetchpattern import *
from salamoia.nacl.searchparser import SearchParser
from salamoia.h2o.flatobject import *
import ldap
import traceback

#from salamoia.nacl.ldap.object import LDAPObject
from salamoia.nacl.flat.object import LDAPObject
from salamoia.nacl.flat.cache import FLATBackendObjectCache
from salamoia.nacl.flat.partialfetcher import FLATPartialFetcher

class FLATBackend(Backend):
    """
    This subclass only redefines the backend control class.
    
    All the intelligence is in the backend control.
    """
    def controlClass(self):
        return FLATBackendModularService

import flatobject

class FLATBackendService(BackendService):
    
    def __init__(self):
        super(FLATBackendService, self).__init__()
        self.searchparser = SearchParser()

        self._fetchAttributes = None

    def checkCredentials(self, user, password, uri=None):
        """
        Check the credentials trying to connect to the ldap directory
        binding as the user.
        """
        
        Ione.log("Checking credentials ... takes time", level=LOG_WARNING)
                
        try:
            # assure we istancied a default connection (pseudo hack)
            Connection.defaultConnection()
            conn = Connection("uid=%s,%s" % (user, Connection.peopleSuffix), password)
        except ConnectionError:
            Ione.log("ConnectionError, checkCredentials failed for user: %s, host %s" %
                     ("uid=%s,%s" % (user, Connection.peopleSuffix), Connection.host))
            return False
        
        return True

    def defaultPartialFetcher(self):
        return FLATPartialFetcher

    def baseFetch(self, id):
        """
        Returns an object matching the given id.

        This kind of search is fast and it does not involve
        search specification objects. It simply searchs for every object
        based at 'id' with scope SCOPE_BASE, thus returning only the
        base DN 'id'.

        After that an object is created from the returning tuples,
        using it's objectclasses to match for a python class,
        and the object's method 'fill' to actually initialize it
        with the data returned from the search.
        """
        Ione.log("FLAT BASE FETCH attributes SLOOOOOOW WHY WHY WHY", self._fetchAttributes, id)

        c = Connection.defaultConnection()
        res = c.search('objectclass=*', base=id,
                       attributes=self._fetchAttributes,
                       scope=ldap.SCOPE_BASE)
        if not res:
            raise FetchError, "Cannot find object"

	
	#        type = LDAPTypeSpec.fromObjectClass(res[0][1]['objectClass'])
	#        if not type:
	#            raise FetchError, "Cannot map object (%s:%s)" % (res[0][0] ,res[0][1]['objectClass'])
	
	#       u = type.toClass()()
	#       u.fill(res[0])
	#       u.type = type

	########
	#return res
	return FlatObject(res[0])

    def search(self, searchSpec):
        """
        Returns a list of object id matching a filter constructed
        from the searchSpec.

        The OwnerSpec specification is used to set the base of the search,
        if it is found inside the spec.
        Otherwise it does a full search.

        TODO: the search could omit all unused attributes from the search...
        """

        
        c = Connection.defaultConnection()

        if type(searchSpec) == type(str()):
            searchSpec = self._parsesearch(searchSpec)
	    Ione.log("Searching parsed:", searchSpec)
	    #try:
	#	res = c.search(searchSpec, attributes=['objectclass'])
	#    except ldap.NO_SUCH_OBJECT:
	#	Ione.log("No such object in %s, %s " % (c.host, c.suffix))
	#	raise
	#else:
	Ione.log("Searching:", searchSpec.filter())
	Ione.log("Scope:", searchSpec.scope())
	Ione.log("Base:", searchSpec.base())
	try:
	    res = c.search(searchSpec.filter(), 
                           scope=searchSpec.scope(),
                           base=searchSpec.base(),
                           attributes=['objectclass']
			   )

	except ldap.NO_SUCH_OBJECT:
	    Ione.log("No such object in %s, %s " % (c.host, c.suffix))
	    raise

        searchResult = [x[0] for x in res]


        ## tmp hack until we can have objects with partial attributes
        if searchSpec.needTrimming():
            objects = self.fetch(searchResult).value
            trimmed = searchSpec.trim(objects)
            return [x.id for x in trimmed]

        return searchResult

    def _parsesearch(self, expr):
        Ione.log("parsing:", expr)
        return self.searchparser(expr)


    def setAttr(self, id, attr, values):
	pass

    def delAttr(self, id, attr):
	pass


    def store(self, object, mode="auto"):
        oldClass = object.__class__
        object.__class__ = LDAPWrapper

        object.store(mode)
        object.__class__ = oldClass
        return 0

    def backendInfo(self, action):

        Info = {
            "salamoia.naclUptime":InfoUptime(self),
            "suffix":InfoSuffix(),
	    "loggedUsers":InfoLoggedUsers(self),
	    "hostname":InfoHostname(self)
            }

        return Info[action]()


class LDAPWrapper(LDAPObject, Object):

    def storableDict(self):
        """
        returns a dictionary with a editable subset of attributes.
        it omits attributes starting with '_' and special attributes 'owner', 'type'
        etc
        """
        specials = ['owner', 'type', 'id', 'acl']
        res = {}
        for i in [a for a in self.attributeNames() if not a in specials]:
            realAttrName = self.reverseAttributeMap.get(i, i)
            res[realAttrName] = getattr(self, i)
        return res

# hack
class FLATBackendModularService(FLATFetchPatternService,
                                FLATBackendObjectCache,
                                BackendMixin, 
                                FLATBackendService):
    pass


class BackendInfo(object):
   def  __init__(self, backend = None):
       if backend:
	   self.backend = backend        

class InfoUptime(BackendInfo):
    def __call__(self):
	now = time.time()
	return now - self.backend.startupTime

class InfoSuffix(BackendInfo):
    def __call__(self):
	return Connection.defaultConnection().suffix

class InfoLoggedUsers(BackendInfo):
    def __call__(self):
	return  self.backend.authControl("getLoggedUsers")

class InfoHostname(BackendInfo):
    def __call__(self):
	return Connection.defaultConnection().host

	 




#Backend.registerBackend("flat", FLATBackend)
