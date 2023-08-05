from salamoia.h2o.flatobject import FlatObject
from salamoia.nacl.flat.object import *
from connection import Connection
from salamoia.nacl.hook import *

class LDAPFlatObject(LDAPObject, FlatObject):

    def store(self, mode):
        #raise NotImplementerError, "non usare direttamente"
        Ione.log("Storing flat object id", self.id)
        FlatObject.store(self, mode)
        Ione.log("LDAP Flat  specific user store actions....")
        LDAPObject.store(self, mode)

    #def computeID(self):
    #    return "%s,%s" % (self.dn, Connection.defaultConnection().suffix)

    def setIdHook(self):
        """
        caused infinite recursion trying to fetch 'owner'
        """
        pass

    def computeID(self):
        """
        since flat have no schema they cannot compute id 
        and the client must suppliy the ID xplicitly
        """

        return self.id


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
