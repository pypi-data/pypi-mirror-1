from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import *
from connection import Connection
from salamoia.nacl.ldap.search import *
from salamoia.h2o.object import *
from salamoia.h2o.container import *


class LDAPFetchPatternService(object):
    """
    this class extends the api offering compact form of frequent called
    base api methods (search & fetch), avoiding unneeded exchange of RPC calls
    """

    def fetchPattern(self, searchSpec, attributes=None):
        """
        Ldap optimized parial fetch.
        If attribes is not specified the superclass implementation
        is called.

        because of attribute name mapping this optimization is only possible
        when the search specification maches only one type
        
        """
        if not attributes:
            return super(LDAPFetchPatternService, self).fetchPattern(searchSpec)

        search = searchSpec
        if type(searchSpec) == type(str()):
            search = self._parsesearch(searchSpec)

        searchType = None
        # check if search spec maps only one type
        if isinstance(search, TypeSpec):
            searchType = search
        elif isinstance(search, AndSpec):
            searchType = search.containsSpecClass(TypeSpec)
        
        if not searchType:
            Ione.log("LDAP FETCHPATTERN: cannot infer the type",searchSpec)
            return super(LDAPFetchPatternService, self).fetchPattern(searchSpec, attributes)

        Ione.log("LDAP SPECIFIC FETCHPATTERN", searchSpec, searchType, attributes)

        mappedAttributes = attributes
        #mappedAttributes = [x for x in attributes] ...

        c = Connection.defaultConnection()
        res = c.search(search.filter(),
                       attributes = mappedAttributes,
                       scope=ldap.SCOPE_BASE)

        objs = [PartialObject(searchType.toClass()().fill(i), attributes) for i in res];
        return Container(objs)


    def fetchOnePattern(self, searchSpec, attributes=None):
        """
        a shorthand combination of search and fetch.
        using it is faster because less requests travel the rpc
        """
        #Ione.log("fetch one pattern", searchSpec)
        return self.fetch(self.searchOne(searchSpec), attributes)

