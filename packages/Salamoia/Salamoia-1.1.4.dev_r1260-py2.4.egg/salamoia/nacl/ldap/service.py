"""
This service manages ldap objects using schemas
"""

from salamoia.nacl.backend import BackendService, BackendMixin
from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import ConnectionError, FetchError
from connection import Connection
from salamoia.h2o.searchparser import SearchParser

from salamoia.nacl.ldap.search import ILdapSearch, TypeSpec
from salamoia.nacl.ldap.schema import LDAPSchema
from salamoia.h2o.schema import ISchema
from salamoia.nacl.ldap.fetchpattern import LDAPFetchPatternService
from salamoia.nacl.auth import IAuthentication

from salamoia.h2o.protocols import multiAdapt

import ldap

__all__ = ['Service']

class LDAPBackendService(BackendService):    
    def __init__(self):
        super(LDAPBackendService, self).__init__()
        self.searchparser = SearchParser()

    def schemaClass(self):
        return LDAPSchema

    def checkCredentials(self, principal, uri=None):
        """
        Check the credentials trying to connect to the ldap directory
        binding as the user.    
        """
        
        Ione.warning("Checking credentials ... takes time")

        # assure we istancied a default connection (pseudo hack)
        Connection.defaultConnection()

        # ensure that schema is loaded
        # self.serviceDescription.schema is lazy and needs to be loaded
        # because it registers the multi-adapters used here 
        # TODO: FIX THIS. it should be done automatically        
        schema = ISchema(self)
        schema.service = self

        ldapUser = multiAdapt((self, principal), IAuthentication).id

        # TODO use this multi adapt syntax:
        #ldapUser = IAuthentication(self, principal).id
        

        Ione.log("ldap user:", ldapUser, msgid='ldapuser')
        try:
            conn = Connection(ldapUser, principal.password)
        except ConnectionError:
            Ione.log("ConnectionError, checkCredentials failed for user: %s, host %s", ldapUser, Connection.host)
            return False
        
        return True

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
        c = Connection.defaultConnection()
        res = c.search('objectclass=*', base=id,
                       scope=ldap.SCOPE_BASE)
        if not res:
            raise FetchError, "Cannot find object"

        type = TypeSpec.fromObjectClass(res[0][1]['objectClass'], self)
        if not type:
            raise FetchError, "Cannot map object (%s:%s)" % (res[0][0] ,res[0][1]['objectClass'])

        u = type.toClass()()
        u._service = self
        u.fill(res[0])
        u.type = type

        return u

    def search(self, searchSpec):
        """
        Returns a list of object id matching a filter constructed
        from the searchSpec.

        The OwnerSpec specification is used to set the base of the search,
        if it is found inside the spec.
        Otherwise it does a full search.

        TODO: the search could omit all unused attributes from the search...
        """

        if isinstance(searchSpec, basestring):
            searchSpec = self._parsesearch(searchSpec)

        searchSpec = ILdapSearch(searchSpec)

        searchSpec.setServiceContext(self)

        Ione.log("Searching:", searchSpec.filter())
        c = Connection.defaultConnection()
        try:
            res = c.search(searchSpec.filter(), attributes=['objectclass'])
        except ldap.NO_SUCH_OBJECT:
            Ione.log("No such object in %s, %s ", c.host, c.suffix)
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

    def test(self, arg, arg2=None):
        Ione.log("called, arg: %s arg2: (%s)", arg, arg2)
        return arg

# hack
class LDAPBackendModularService(LDAPFetchPatternService,
                                BackendMixin, 
                                LDAPBackendService):
    pass

# TODO: rename the class
Service = LDAPBackendModularService


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
