"""
This is one of the most bloated modules of salamoia

Basically it contains the base class for all salamoia objects, splitted in two
classes: BaseObject and Object

"""

from salamoia.h2o.exception import ReadOnlyError
from salamoia.h2o.attribute import Attribute
from salamoia.h2o.acl       import AllowACE, ReadAction, WriteAction
from salamoia.h2o           import acl

from protocols import Interface, advise, protocolForURI
import types

class IObject(Interface):
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/IObject')])

class BasicObject(object):
    """
    Base class for all objects that are shared between the backend and
    the frontend.

    It handles very complex migration and transmutation using
    advanced python reflection techniques.

    (This is no more true: now its flatten out in a xmlrpc dictionary see salamoia.h2o.xmlserver)

    It also dinamically handles the attribute dictionary
    and the access control.

    An object is identified with an ID. But this ID
    in some backends (LDAP) needs to be computable from the contents
    of the object (see computeId())

    The object contains an attribute dictionary
    maintaining an instance of Attribute class for every
    other instance variable. Subclasses can define
    how to map specific attribute names to specific Attribute sublcasses,
    setting the mapping in the _attributeTypeMap class variable.
    (see Attribute)

    access control is set
    """
    _attributeTypeMap = {'acl': types.ACL()}

    objectClasses = {}
    attributeMap = {}
    reverseAttributeMap = {} ## automated

    keyAttribute = None
    
    def __init__(self, id=""):
        """
        It creates a new empty object, optionally given an ID
        """

        super(BasicObject, self).__init__()
        self.owner = None
        self.acl = acl.ACL()
        self.type = None
        self.id = id

        #Ione.log("BasicObject initialized")

    def __setattr__(self, name, value):
        """
        This is a real mess. (with a reasion)

        This method catches all instance variable assignment
        and automatically does magic while maintaining
        the ease of use in subclasses.

        The main magic is the dinamic attribute mapping creation.
        The Attribute instance will be created only on first
        assignment. After it all updates are directed in the
        attribute object (caching them in the object itself)

        The other magic is the automatic adding of 'itself' to
        the acl. Allwing an object to have full access of itself
        without that information being written explicitly
        in the repositroy.
        """
        
        # lazy instantiation of attribute dictionary
        if not "_attributes" in self.__dict__:
            self.__dict__["_attributes"] = {}
            
        object.__setattr__(self, name, value)
        if name == "__class__":
            return
        
        if not self._attributes.has_key(name):
            self._attributes[name] = Attribute(name, value, self.mapAttributeType(name))
        else:
            self._attributes[name].value = value
        
        if name == 'id':
            if value:
                if hasattr(self, 'setIdHook'):
                    self.setIdHook()
                if hasattr(self, 'acl'):
                    from salamoia.nacl.auth import IAuthentication
                    try:
                        auth = IAuthentication(self)
                        #print '====================================='
                        #print "ADAPTED TO IAUTHENTICATION", self
                        #print '====================================='
                        self.acl.append(AllowACE(self.id, [ReadAction(), WriteAction()]))
                    except TypeError:
                        #print '====================================='
                        #print "CANNOT ADAPT", self, "TO IAuthentication"
                        #print '====================================='
                        pass

        if name == self.keyAttribute:
            #Ione.log("setting key attribute to", value)
            if value:
                self.computeID()

    def mapAttributeType(self, name):
        """
        return the type instance associated with a given attribute name
        """
        if name in self._attributeTypeMap:
            return self._attributeTypeMap[name]
        return types.String()

    def computeID(self):
        return None

    def __repr__(self):
        attrs = {}
        for k in self.__dict__:
            if not k.startswith('_'):
                attrs[k] = self.__dict__[k]
        
        from pprint import pformat
        return "%s(%s)" % (self.__class__, pformat(attrs))

    def checkAcl(self, id, action):
        """
        wrapper around acl.check.
        """
                
        return self.acl.check(id, action)

    def attributeNames(self):
        """
        return only instance variable names which doesn't start with
        underscore.

        TODO: move to attribute list
        """
        return [a for a in self.__dict__ if not a.startswith('_')]

    def editableDict(self):
        """
        returns a dictionary with a editable subset of attributes.
        it omits attributes starting with '_' and special attributes 'owner', 'type'
        etc
        """
        specials = ['owner', 'type', 'id']
        res = {}
        for i in [a for a in self.attributeNames() if not a in specials]:            
            res[i] = self._attributes[i].display()
        return res

    def inspectableDict(self):
        """
        like editable dict but returns raw values instead of strings
        """
        specials = ['owner', 'type', 'id']
        res = {}
        for i in [a for a in self.attributeNames() if not a in specials]:            
            res[i] = self._attributes[i].value
        return res

    def storableDict(self): ## TODO merge with editableDict
        """
        returns a dictionary with a editable subset of attributes.
        it omits attributes starting with '_' and special attributes 'owner', 'type'
        etc
        """
        specials = ['owner', 'type', 'id', 'acl']
        res = {}
        for i in [a for a in self.attributeNames() if not a in specials]:
            realAttrName = self.reverseAttributeMap.get(i, i)
            res[realAttrName] = self._attributes[i].store()

        return res

    def createChild(self, cls):
        """
        Simply instantiates an istance of the given class and sets self as its owner
        """
        obj = cls()
        obj.owner = self
        return obj

    def resurrect(self):
        """
        Called after the passage of the object through xmlrpc

        Used to insert postprocessing code, like owner reconstruction etc
        """
        return self
    
    def junkCheck(self):
	"""
        (Rename to 'validate' or something like that)

	redefine in subclasses if you want to check for junk in fields.
	
	raises an exception if found junk in at least one attribute
	"""
	for i in self._attributes.values():            
            i.junkCheck()
    
class Object(BasicObject):
    """
    For some, now unknown, reasions the implementation split the Object class in two classes (Object and BasicObject)
    """
    advise(instancesProvide=[IObject])

    def __getitem__(self, attr):
        """
        Useful in Zope Page Templates because of security restrictions of using __dict__
        """        
        return self.__dict__[attr]
    
class ReadOnlyObject(Object):
    """
    This class prevents write to attributes
    """
    def __setitem__(self, name, value):
        raise ReadOnlyError

class PartialObject(ReadOnlyObject):
    """
    Will be obsoleted

    This class describes objects with only parial attributes.

    It was generated on the server side and used alyways on the client side, so now with the new
    xmlrpc standard is no more useful and will be obsoleted

    """

    def __init__(self, obj, attributes):
        for a in attributes:
            self.__dict__[a] = getattr(obj, a)
        #Ione.log("Partial object", self.__dict__)

    def __repr__(self):
        return "PartialObject(%s)" % (self.inspectableDict())

    def inspectableDict(self):
        d = dict(self.__dict__)
        if d.has_key('_attributes'):
            del d['_attributes']
        return d

#from xmlclient import Client

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
