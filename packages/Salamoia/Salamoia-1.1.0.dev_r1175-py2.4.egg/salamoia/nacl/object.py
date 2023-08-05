from salamoia.h2o.object import Object
from salamoia.nacl.backend import Backend
from salamoia.h2o.exception import *
from salamoia.h2o.logioni import Ione
import salamoia.h2o.acl
from salamoia.h2o.attribute import *
import timing
import sys

#class NACLObject(object):
class NACLObject(Object):
    hookMap = {}
    creationHooks = []
    modificationHooks = []
    
    def fetchOwner(self):
        c = Backend.defaultBackend().control
        try:
            # if the object's container is a singleton don't fetch 
            # TODO: make singleton behave like normal objects ... but singleton
            if self.schema.containerClass.schema.absoluteDN():
                return None
            res =  c.fetch(self.ownerId())
            return res
        except FetchError:
            print "FEEEEEEEEETCH EEEEEEEEEEEEEEEEEERRROR", sys.exc_type, sys.exc__value
            pass
        except:
            print "EXCEPTION", sys.exc_type, sys.exc_value            
        

    def ownerId(self):
        raise NotImplementedError, "to be overriden"

    def setIdHook(self):
        self.owner = self.fetchOwner()
        if self.owner:
            for i in self.owner.acl:
                self.acl.append(i) # TODO: maybe a copy is better?

    def typeSpec(self):
        raise NotImplementedError, "to be overriden"

    def __getstate__(self):
        Ione.log("GETTING STATE for pickle")
        return self.__dict__

    def __getattr__(self, name):
        #timing.start()
        #Ione.log("CALLING NACL GETATTR in", self.__class__, name)
        if name == '_attributes':
            state = self.__dict__
            attrs = {}
            for name in [x for x in state if x[0] != '_']:
                attrs[name] = Attribute(name, state[name], self.mapAttributeType(name))
            state['_attributes'] = attrs 
            #timing.finish()
            #Ione.log("GETATTR took msec:", timing.milli())
            return attrs
        # perche non c'era questa prima?
        try:
            return self.__dict__[name]
        except:
            raise AttributeError, name

    def __setstate__(self, state):
        Ione.log("CALLING NACL setstate in", self.__class__)
        # you can do better ...

        state['acl'] = h2o.acl.ACL()
        self.__dict__ = state
