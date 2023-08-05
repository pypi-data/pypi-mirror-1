"""
This is one of the most bloated modules of salamoia

Basically it contains the base class for all salamoia objects, splitted in two
classes: BaseObject and Object

In older versions it handled the pickling and unpikling and now should be cleaned

"""

from reflection import ClassExtender, ClassNamed
from logioni import *
from syslog import *
import acl
from salamoia.h2o.acl import *
from salamoia.h2o.exception import *
from pickle import Pickler,Unpickler
import cPickle
from cStringIO import StringIO
import traceback
from attribute import *
import types

class ConversionPickler(Pickler):
    """
    Obsolete

    pickles redirection Object subclassess according to
    ClassExtender's mapping
    """
    def save(self, obj):
        if isinstance(obj, Object):            
            oldClass = obj.__class__
            obj.__class__ = ClassExtender.inverseClassRedirect(oldClass)
            Pickler.save(self, obj)
            obj.__class__ = oldClass
        else:
            Pickler.save(self, obj)
        

class ConversionUnpickler(Unpickler):
    """
    Obsolete

    unpickles redirection Object subclassess according to
    ClassExtender's mapping
    """
    def find_class(self, module, name):
        oldClass = Unpickler.find_class(self, module, name)
        return ClassExtender.classRedirect(oldClass)

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
    
    def __new__(cls, *args):
        """
        This techique allows to transmutate the class according
        to the current ClassExtendes's redirection table.

        This tick allows the client to have an instance of h2o.user.User
        for example and when it comes out through the RPC channel
        it pops out magically as a nacl.ldap.user.LDAPUser ....

        This completely hides any implementation detail from the client,
        and allows many backend implementation, while maintaing the logic
        in the object themselves (an OO approach)
        """
        return ClassExtender.new(object, cls, args)
    
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
                try:
                    self.setIdHook()
                    # ignore if setIdHook doesn't exist
                except AttributeError:
                    pass
                if hasattr(self, 'acl'):
                    self.acl.append(AllowACE(self.id, [ReadAction(), WriteAction()]))

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
        return "%s(%s)" % (self.__class__, str(self.__dict__))

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

    def pickle(cls, obj, dir):
        """
        Obsolete

        Does the serialization needed to transport the object through the RPC
        """
        s = StringIO()
        p = {cls.CLIENT_TO_SERVER: Pickler, cls.SERVER_TO_CLIENT: ConversionPickler}[dir](s)
        p.dump(obj)
        return s.getvalue()

    pickle = classmethod(pickle)

    def unpickle(cls, string, dir):
        """
        Obsolete

        Does the deserialization needed to get the object from the RPC
        """

        s = StringIO(string)
        un = {cls.CLIENT_TO_SERVER: ConversionUnpickler, cls.SERVER_TO_CLIENT: Unpickler}[dir](s)
        try:
            obj = un.load()
        except:            
            Ione.log("DIO CANEEEEEEEEEEEEEEEEEEEEEEEEE", level=LOG_ERROR)
            obj = None
            traceback.print_exc()
            raise
        return obj.resurrect()

    unpickle = classmethod(unpickle)

    def resurrect(self):
        return self
    
    def junkCheck(self):
	"""
        (Rename to 'validate' or something like that)

	redefine in subclasses if you want to check for junk in fields.
	
	raises an exception if found junk in at least one attribute
	"""
	for i in self._attributes.values():            
            i.junkCheck()

    def pickledEncapsulation(cls, obj, dir):
        """
        Obsolete
    
        Some native objects are automatically passed through XMLRPC.
        In order to distinguisc pikled object from string, list and dictionries,
        the pikled object is implemented as a dictionary containing a '__magic__'
        field containting a magic constant and a string containing the pickled data
        """
        return {'__magic__': cls.__pickleMagic, 'object': cls.pickle(obj, dir=dir)}

    pickledEncapsulation = classmethod(pickledEncapsulation)

    def isPickled(cls, obj):
        """
        Obsolete
        """
        try:
            if obj.get('__magic__') == cls.__pickleMagic:
                return True
        except AttributeError:
            pass

    isPickled = classmethod(isPickled)

    def decapsulePickled(cls, dict, dir):
        """
        Obsolete
        """
        return cls.unpickle(dict['object'], dir=dir)

    decapsulePickled = classmethod(decapsulePickled)

    # obsolete
    __pickleMagic = "__piRiPipPick1e__"

    # obsolete
    CLIENT_TO_SERVER = "client_to_server"
    # obsolete
    SERVER_TO_CLIENT = "server_to_client"
        

# obsolete
def cPickle_load_global(modulename, classname):
    return ClassExtender.classRedirectNamed(modulename + '.' + classname)
    
class Object(BasicObject):
    """
    For some, now unknown, reasions the implementation split the Object class in two classes (Object and BasicObject)
    """
    
    def __getitem__(self, attr):
        """
        Useful in Zope Page Templates because of security restrictions of using __dict__
        """        
        return self.__dict__[attr]
    
    def pickle(cls, obj, dir):
        """
        Obsolete

        Does the serialization needed to transport the object through the RPC
        """
        #Ione.log("Pickling")
        s = StringIO()

        ## working method
        #p = {cls.CLIENT_TO_SERVER: cPickle.Pickler,
        #     cls.SERVER_TO_CLIENT: ConversionPickler}[dir](s)

        ## doesn't work because cpickle cannot handle class trasmutation
        #p = {cls.CLIENT_TO_SERVER: cPickle.Pickler,
        #     cls.SERVER_TO_CLIENT: cPickle.Pickler}[dir](s)

        ## new compacting method using __getstate__
        p = {cls.CLIENT_TO_SERVER: ConversionPickler,
             cls.SERVER_TO_CLIENT: ConversionPickler}[dir](s, protocol=2)
        p.dump(obj)
        return s.getvalue()

    pickle = classmethod(pickle)

    def unpickle(cls, string, dir):
        """
        Does the deserialization needed to get the object from the RPC
        """
        #Ione.log("UnPickling")
        s = StringIO(string)
        #un = {cls.CLIENT_TO_SERVER: ConversionUnpickler,
        #      cls.SERVER_TO_CLIENT: cPickle.Unpickler}[dir](s)

        ## working method
        un = {cls.CLIENT_TO_SERVER: cPickle.Unpickler,
              cls.SERVER_TO_CLIENT: cPickle.Unpickler}[dir](s)

        un.find_global = cPickle_load_global
        try:
            obj = un.load()
        except:            
            Ione.log("GOD PIGGGGGGGG", sys.exc_value)
            obj = None
            traceback.print_exc()
            raise
        return obj.resurrect()

    unpickle = classmethod(unpickle)

    def __getstate__(self):
        """
        Obsolete, pickling
        """

        trimmed = self.__dict__.copy()

        #if trimmed.has_key('_attributes'):
        #    del trimmed['_attributes']
        if trimmed.has_key('acl'):
            del trimmed['acl']
        #if trimmed.has_key('type'):
        #    del trimmed['type']

        #Ione.log("H2O GETTING STATE for pickle", self.__class__, trimmed)
        #Ione.log("------------")
        return trimmed

    #def __setstate__(self, state):
    #    Ione.log("CALLING H2O setstate in", self.__class__)

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
