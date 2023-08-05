from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import *
from salamoia.h2o.attribute import *
import re

__all__ = ['Type', 'String', 'List', 'ACL', 'Integer', 'Boolean', 'UencodedString', 'Password', 'MailString']

class Type(object):
    """
    A type defines how to map from a backend (ldap) rapresentation to a in memory rapresentation
    """
    
    def __init__(self):
        pass
    
    def storeFormat(self, attribute):
        """
        implementation specific subclasses should implement this.
        returns the string (or other implementation specific object) used for storing
        """
        #raise NotImplementedError, "to be overriden"
        return self.displayFormat(attribute)

    def displayFormat(self, attribute):
        """
        subclasses can implement this.
        returns the string used for textual of the displaying the object .
        """
        return str(attribute.value)

    def transformValue(self, value):
        if len(value) == 1:
            return value[0]
        return value
    
    def junkCheck(self, value):
	pass

    def defaultValue(self):
        return None

class String(Type):
    def storeFormat(self, attribute):
        if attribute.value == None:
            return None
        return self.displayFormat(attribute)

class List(Type):
    """
    The most commonly used type (besides the default String) is the List type, mostly because of 
    the fact that ldap protocol (and the ldap interface module) returns lists even when the ldap schema defines a single attribute.

    If the default 'transformValue' implementation, which reduces lists of length one to simple values is not appropriate, then use 
    a List type, which will always rapresent the value as a list.
    """

    def __init__(self, itemType = String()):
        """
        The optional itemType argument to the constructor allows you to constrain the types of the contained elements
        """
        Type.__init__(self)
        self.itemType = itemType
    
    def storeFormat(self, attribute):
        """
        accepts a list of attributes
        """
        if not isinstance(attribute.value, list):
            raise "this type must contain a list of objects (not %s)" % attribute.value

        return [str(a) for a in attribute.value]
        #return [Attribute("tmp", a, self.itemType).store() for a in attribute.value]

    def displayFormat(self, attribute):
        """
        accepts a list of attributes
        """
        if not isinstance(attribute.value, list):
            raise "this type must contain a list of objects (not %s)" % attribute.value            
        #return ', '.join([a.type.displayFormat(a.value) for a in attribute.value])
        return ', '.join([str(a) for a in attribute.value])

    def transformValue(self, value):
        return value

    def junkCheck(self, value):
        for i in value:
            self.itemType.junkCheck(i)

    def defaultValue(self):
        return []

class ACL(List):
    pass

class Integer(Type):
    """
    TODO: convert to integer
    """

class Boolean(Type):
    """
    TODO: do something! check something!
    """

class UencodedString(String):
    pass

# todo: decouple
from salamoia.nacl.ldap.password import *

class Password(UencodedString):
    def storeFormat(self, attribute):
        """
        if the value is not already encripted then encript it.
        encripted values begins with {encoding}' where encoding
        is usually SSHA.
        """
        if not attribute.value:
            return attribute.value
        if attribute.value[0] == '{':
            return attribute.value
        return PasswordHasher(attribute.value).hash()

class MailString(Type):
    """
    This type checks if a mail has a valid format
    """
    def junkCheck(self, value):
	components = value.split("@")
	if len(components) != 2:
	    raise JunkInMailStringError
	for c in components:
            if not re.match('[a-zA-Z0-9\-\._]+$', c):
		raise JunkInMailStringError
		
	
