from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import *
from connection import Connection
from salamoia.h2o.search import *
from salamoia.h2o.object import *
from salamoia.h2o.container import *

from salamoia.nacl.flat.object import *
from salamoia.nacl.flat.flatobject import *

class FLATFetchPatternService(object):
    """
    this class extends the api offering compact form of frequent called
    base api methods (search & fetch), avoiding unneeded exchange of RPC calls
    """

    def fetchPattern(self, searchSpec, attributes=None):
        """
        Ldap optimized parial fetch.
        
        """

        Ione.log("FLAT SPECIFIC FETCHPATTERN", searchSpec, attributes)

        search = searchSpec
        if type(searchSpec) == type(str()):
            search = self._parsesearch(searchSpec)

        #print "LDAP SEARCH", search.filter(), mappedAttributes

        c = Connection.defaultConnection()
        res = c.search(search.filter(),
                       attributes = attributes,
                       base=search.base(),
                       scope=search.scope())

        if attributes:
            objs = [PartialObject(LDAPFlatObject(i), attributes) for i in res];
        else:
            #objs = [LDAPFlatObject().fill(i) for i in res];
            objs = [LDAPFlatObject(i) for i in res];

        if search.needTrimming:
            objs = search.trim(objs)
        
            
        return Container(objs)


    def fetchOnePattern(self, searchSpec, attributes=None):
        """
        a shorthand combination of search and fetch.
        using it is faster because less requests travel the rpc
        """
        #Ione.log("fetch one pattern", searchSpec)
        return self.fetch(self.searchOne(searchSpec), attributes)


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
