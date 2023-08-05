from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *
from salamoia.nacl.backend import Backend
from salamoia.h2o.search import *
from salamoia.h2o.config   import Config
import os, sys

class Hook(object):
    def __init__(self):
        pass

    def storeAttribute(self, object, name, values):
        """
        called before storing an object.
        does nothing if the value is accepted
        otherwise raises an exception
        describing the error

        values is a list of the attribute values
        """
        raise NotImplementedError, "must override"

    def storeObject(self, object):
        pass

    def postStoreObject(self, object):
	pass



class GenericLimitHook(Hook):
    def __init__(self, limitName, counter, rooter=None):
        """
        'rooter' is a lambda function which returns the actual
        object where to search for a field named 'limitName' given the
        leaf object (for example 'get the user associated with a virtualMailUser)

        -1 means infinite
        """
        self.limitName = limitName
        self.counter = counter
        self.rooter = rooter
        
    def storeAttribute(self, object, name, values):
        rootObject = object
        if self.rooter:
            rootObject = self.rooter(object)

        # -1 means infinite
        if int(getattr(rootObject, self.limitName)) == -1:
            return
        
        if self.counter(values) > int(getattr(rootObject, self.limitName)):
            raise LimitExceededError, "Troppi attributi fanno male"

        
class ContainerLimitHook(Hook):
    """
    Checks that the user owns a limited number of objects
    containing this hook. The limit name is defined in the
    'limitName' parameter to the constructor.
    """
    
    def __init__(self, limitName, rooter=None):
        """
        'rooter' is a lambda function which returns the actual
        object where to search for a field named 'limitName' given the
        leaf object (for example 'get the user associated with a virtualMailUser)
        """
        self.limitName = limitName
        self.rooter = rooter

    def countExisting(self, object):
        rootObject = object.owner
        if self.rooter:
            rootObject = self.rooter(object)

        spec = AndSpec([object.typeSpec(), OwnerSpec(object.owner.id)])
        res = Backend.defaultBackend().control.search(spec)
        
        return len(res)
    
    def storeObject(self, object):
        rootObject = object.owner
        if self.rooter:
            rootObject = self.rooter(object)

        # -1 means infinite
        if int(getattr(rootObject, self.limitName)) == -1:
            return
            
        if self.countExisting(object) >= int(getattr(rootObject, self.limitName)):
            raise LimitExceededError, "Troppi oggetti fanno male"

from salamoia.nacl.backend import Backend

class AvoidDuplcationHook(Hook):
    def __init__(self, ty):
        self.type = ty

    def storeObject(self, object):
        key = object.keyAttribute
        ldapkey = object.reverseAttributeMap.get(key, key)
        spec = AndSpec([TypeSpec(self.type), PropSpec(ldapkey, getattr(object, key))])
        existing = Backend.defaultBackend().control.search(spec)
        Ione.log("existing", existing)
        
        if existing:
            Ione.log("ESISTE ERRORE...")
            raise StoreAlreadyExistsError, "Esiste gia'"

class GenericScriptHook(Hook):
    def __init__(self, script):
	self.script = script

    def execute(self):
	raise NotImplementedError, "must override"
	
    def postStoreObject(self, object):
	pass

class GenericPythonScriptHook(GenericScriptHook):

    """
    args must be a dictionary with the vars for the 
    python script 

    """
    
    # refactor this!! take the script name as parameter, to include in nacl/xxx/yyy.py object
    def __init__(self, scriptName=None):
        self.scriptName = scriptName
        self.args = {}

    def execute(self):
        self.scriptPath = Backend.defaultBackend().scriptPath()
        self.rootPath = Backend.defaultBackend().rootPath()
        self.args["SCRIPTSDIR"] = self.scriptPath
        self.args["ROOTDIR"] = self.rootPath
        self.args["CONTROLLER"] = Backend.defaultBackend().control

        # ignore the script if the path is not set 
        if not self.scriptName:
            return 1
        
	try:
	    code = file(os.path.join(self.scriptPath, self.scriptName), 'r')
	except:
	    raise
	
	Ione.log("Executing script")
	try:
	    exec code in self.args
	except:
            Ione.log("script failed with", sys.exc_value)
            raise
	code.close()
	return 1
    
    def postStoreObject(self, object):
	
	self.args["OBJECT"]  = object
	if self.execute():
	    return
	else:
	    return None

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.scriptName)

class AttributePropagationHook(Hook):
    """
    this hook propagates the value of an attribute to a selected subset of child
    objects
    """
    def __init__(self, pattern):
        super(AttributePropagationHook, self).__init__()
        
        self.pattern = pattern

    def storeAttribute(self, object, name, values):
        Ione.log("propagating attribute", name, values)
        controller = Backend.defaultBackend().control
        
        childIDs = controller.search("owner='%s' and (%s)" % (object.id, self.pattern))
        Ione.log("matching children", childIDs)

        # maybe do this generic in store....
        value = object.mapAttributeType(name).transformValue(values)

        for cid in childIDs:
            child = controller.fetch(cid)
            setattr(child, name, value)
            child.store("modify")

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
