"""
This module contains salamoia specific exception classes
"""

from reflection import ClassNamed

import sys

class SalamoiaException(Exception):
    """
    This is the base class for all salamoia exceptions.
    It is useful because it can unwrap xmlrpc wrapped faults.
    """

    @classmethod
    def matches(cls):
        return cls.matchesName(ClassNamed.className(cls))

    @staticmethod
    def matchesName(name):
        try:
            return name in str(sys.exc_type) or name in sys.exc_value.faultString
	except:
	    return False

    @staticmethod
    def message():
        exc = sys.exc_value
	#if  isinstance(exc, xmlrpc.fault):
	#   return (''.join(exc.faultString.split(":")[1:]))[1:]
        try:
            return exc.faultString
        except:
            return str(exc)

class ObsoleteException(SalamoiaException):
    """
    Raised when callilng an obsolete function
    """

class ReadOnlyError(SalamoiaException):
    """
    Raised when an attribute is read only and was written
    """

class SearchError(SalamoiaException):
    """
    Raised when an error occoured while searching
    """

class FetchError(SalamoiaException):
    """
    Raised while fetching an object
    """

class StoreError(SalamoiaException):
    """
    Raised while storing an object
    """

class StoreCreateError(StoreError):
    """
    Raised while creating a new object
    """

class StoreAlreadyExistsError(StoreCreateError):
    """
    Riased when storing an object in 'create' mode and the object altready exists
    """

class StoreModifyError(StoreError):
    """
    Riased when storing an object in 'modify' mode and the object don't exists
    """

class ConnectionError(SalamoiaException):
    """
    Connection error
    """

class AuthenticationError(ConnectionError):
    """
    Raised when the authentication credentials are incorrect
    """

class EmptyPasswordError(ConnectionError):
    pass

class VFSError(SalamoiaException):
    pass

class InvalidPathError(VFSError):
    pass

class ProtocolError(SalamoiaException):
    pass

class FormatError(SalamoiaException):
    pass

class LimitExceededError(SalamoiaException):
    """
    Raised when an object is created over the limits specified in the db
    """
    pass

class JunkError(SalamoiaException):
    """
    Raised when an attribute doesn't match the type
    """
    pass

    
class JunkInMailStringError(JunkError):
    """
    Raised when a email attribute doesn't match a email format

    REFACTOR
    """
    pass

class TransactionError(SalamoiaException):
    pass

class TransactionDoesNotExistError(TransactionError):
    pass

class ScriptError(SalamoiaException):
    """
    Raised when a script terminates with an error
    """

class HandledError(SalamoiaException):
    """
    error which is already catched and handled
    but can be rethrown for exiting nested constructs
    """
    pass

class ServiceException(SalamoiaException):
    """
    Exception caused while executing service related routines
    """
    pass

class ServiceNotFoundException(ServiceException):
    """
    The given uri doesn't match a registered service
    """
    pass

class ServiceDoesNotImplementException(ServiceException):
    """
    The given method is not implemented
    """
    pass

class XMLException(SalamoiaException):
    """
    Exception during parsing of xml
    """

class UnknownXMLChildException(XMLException):
    """
    xmlparser based parser elements found a child element that is not implemented
    """

class TransformationError(SalamoiaException):
    """
    Raised when the xmlserver fails to transform complex objects in primitive types
    """

class TransactionDoesNotExistException(SalamoiaException):
    """
    Obsolete
    """

class SecurityException(SalamoiaException):
    """
    Base for security exceptions
    """

class BadAceFormatException(SecurityException):
    """
    Raised when the ace string format is wrong
    """

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
