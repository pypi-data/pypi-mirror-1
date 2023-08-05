from salamoia.nacl.object import NACLObject
from salamoia.nacl.ldap.ldapbackend import LDAPBackend
from salamoia.h2o.logioni import Ione
from salamoia.h2o.types import Type
from salamoia.nacl.search import TypeSpec
from salamoia.h2o.exception import *

from connection import Connection
from ldap import MOD_ADD, MOD_DELETE, MOD_REPLACE
import ldap, ldap.modlist

import sys

class LDAPObject(NACLObject):    
    def fill(self, list):
        """
        Fills the object from the ldap search result
        directly in instance variables of the same name.

        When an attirbute has many values it will be stored
        as a list. When it has only one value it will be stored
        as single value.

        TODO: this will be ovverrideable with some kind of 'mapping' table
        which says that some attribute names are always 'list', in order
        to simplify the code elsewhere.
        """

	base = list
        self.id = base[0]
        dict = base[1]

        specials = ['objectClass']
        #for i in filter(lambda x: not x in specials, dict.keys()):
        for i in [x for x in dict if x not in specials]:
            val = dict[i]
            attribute = self.attributeMap.get(i, i)
            type = self._attributeTypeMap.get(attribute, Type())
            val = type.transformValue(val)
            setattr(self, attribute, val)
        
        return self

    def store(self, mode):
        """
	-
	un po' grezza l'implementazione, per correggere un bug che 
	permetteva ad un eccezzione 'limit' di far fare 'add' invece di 'modify'
        """
        Ione.log("Generic FLAT LDAP store (%s)" % (self.id))

        if mode == "auto" or mode == "modify":
            try:
                orig = Connection.defaultConnection().search("objectclass=*", base = self.id)[0][1]
                operation = "modify"
            except:
                Ione.log("Tried Modify store but got exception", sys.exc_value)
                if mode == "modify":
                    raise
                operation = "create"
        else:
            operation = mode

	if operation == "modify":
	    return self._storeModify(orig)
	elif operation == "create":
	    return self._storeAdd()
        else:
            raise StoreError, "invalid mode %s" % (operation)
        
    def _storeAdd(self):
	Ione.log("FLAT LDAP store ADD\n-----------------")
        # checking limits on store
        for i in self.creationHooks:
            i.storeObject(self)
        
        # Normalize values (all values must be lists)
        dict = self.storableDict()
        for i in dict:
            if not isinstance(dict[i], type([])):
                dict[i] = [dict[i]]
        Ione.log("Add Dict:", dict)
        # creating modlist for ldap add
        #modlist = ldap.modlist.addModlist(dict,
        #                                  ignore_attr_types =
        #                                  self.ignoredStoreAttributes())
        if self.objectClasses:
            dict.update({"objectclass": self.objectClasses})
        modlist = ldap.modlist.addModlist(dict)
        
        Ione.log("Add Modlist: ", modlist)

        try:
	    Ione.log("ID in store ADD:" + str(self.id))
	    Ione.log("modlist: in store ADD" + str(modlist))
            Connection.defaultConnection().basicAdd(self.id, modlist)
            Ione.log("added successfully. now calling hooks")
            try:
                for i in self.creationHooks:
                    Ione.log("calling hook", i)
                    i.postStoreObject(self)
            except:
                Ione.log("aborting add (deleting newly created %s)" % (self.id))
                Connection.defaultConnection().basicDelete(self.id)
                raise

	except ldap.ALREADY_EXISTS:
            raise StoreAlreadyExistsError

    def _storeModify(self, orig):
	Ione.log("LDAP store MODIFY\n-----------------")

        # checking limits on store
        for i in self.modificationHooks:
            i.storeObject(self)

        Ione.log("Orig: ", orig)

        # normalize values (all values must be lists)
        sdict = self.storableDict()
        dict = {}
        for i in sdict:
            if sdict[i]:
                dict[i] = sdict[i]
            else:
                continue
            if not isinstance(dict[i], type([])):
                dict[i] = [dict[i]]

        if self.objectClasses:
            dict.update({"objectclass": self.objectClasses})
        Ione.log("Dict: ", dict)

        # creating modlist for ldap modify
        modlist = ldap.modlist.modifyModlist(orig, dict,
                                             ignore_attr_types =
                                             self.ignoredStoreAttributes())

        # applying hooks

        Ione.log("looking in hookmap", self.hookMap, "attributes", [x[1] for x in filter(lambda x: x[0]==0, modlist)])
        for i in [x[1] for x in filter(lambda x: x[0]==0, modlist)]:
            attributeName = self.attributeMap.get(i, i)
            Ione.log("searching hook for", attributeName)
            for hook in self.hookMap.get(attributeName, []):
                Ione.log("calling hook", hook)
                hook.storeAttribute(self, attributeName, dict[i])

        try:
            for i in self.modificationHooks:
                Ione.log("calling hook", i)
                i.postStoreObject(self)
        except:
            raise

        Ione.log("Modlist: ", modlist)

        # do the modify
        Connection.defaultConnection().basicModify(self.id, modlist)

    def delete(self):
        Ione.log("DELETING OBJECT %s (real)" % (self.id))
        Connection.defaultConnection().basicDelete(self.id)

    def ignoredStoreAttributes(self):
        """
        returns a list of attributes that will be ignored on store
        """
        #return ["objectClass"]
        return []

    def ownerId(self):
        """
        Compute the id of the parent object
        """
        return ",".join(self.id.split(",")[1:])

    def computeID(self):
        #raise NotImplemented, "computeID"
        try:
            #Ione.log("computing ID for generic ldap (owner)" )
            k = self.keyAttribute
            keyAttribute = self.reverseAttributeMap.get(k, k)
	    ## qui non va una minkia
	    return "%s=%s,%s" % (keyAttribute, self.__dict__[self.keyAttribute], self.owner.id)
	    #return None
	except AttributeError:
            pass
#raise
        return None

    def resurrect(self):
        newID = self.computeID()
        Ione.log("Resurrecting", self.__class__, self.id, newID)
        
        if newID != self.id:
            self.id = newID # trigger fetch of eventual new parent

        return self
            
        
    def typeSpec(self):
        return TypeSpec.fromObjectClass(self.objectClasses)
