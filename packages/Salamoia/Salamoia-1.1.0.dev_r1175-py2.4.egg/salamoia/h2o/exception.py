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

    def matches(cls):
        return cls.matchesName(ClassNamed.className(cls))

    matches = classmethod(matches)

    def matchesName(cls, name):
        try:
            return name in str(sys.exc_type) or name in sys.exc_value.faultString
	except:
	    return False

    matchesName = classmethod(matchesName)

    def message(cls):
        exc = sys.exc_value
	#if  isinstance(exc, xmlrpc.fault):
	#   return (''.join(exc.faultString.split(":")[1:]))[1:]
        try:
            return exc.faultString
        except:
            return str(exc)

    message = classmethod(message)

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
