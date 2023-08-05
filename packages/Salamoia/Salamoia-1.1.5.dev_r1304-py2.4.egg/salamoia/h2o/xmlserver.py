import xmlrpclib

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import base64

from salamoia.h2o.logioni import Ione
from salamoia.h2o.object import Object, IObject
from salamoia.h2o.exception import TransformationError
from salamoia.h2o.auth import Principal, IAuthenticatedPrincipal

import string
import threading
import sys, traceback

from protocols import adapt, declareAdapter, protocolForURI, Interface, advise, NO_ADAPTER_NEEDED
types = __import__('types')
from salamoia.h2o.functional import partial


__all__ = ['Server']


class Unmarshaller(xmlrpclib.Unmarshaller):
    _super = xmlrpclib.Unmarshaller

    def end_struct(self, data):
        """
        Dictionaries are adapted to INativeTransportedObject protocol
        """
        res = self._super.end_struct(self, data)
        val = self._stack[-1]
        self._stack[-1] = adapt(val, INativeTransportedObject, val)

        return res
    _super.dispatch['struct'] = end_struct

class Marshaller(xmlrpclib.Marshaller):
    """
    Specialized salamoia xmlrpc marshaller.
    Since xmlrpclib.dumps hardcodes allow_none = 0 we force it here
    so that there is no need of redefining the longer "marshaled_dispatch".
    
    The values are adapted to ITransportedObject before encoding them.
    
    """

    _super = xmlrpclib.Marshaller
    def __init__(self, enc, allow=True):
        """
        Force allow none
        """
        self._super.__init__(self, enc, True)

    def __dump(self, value, write):
        """
        The original xmlrpclib.Marshaller.__dump method looks up the type of 'value'
        in a dictionary and executes the callable found there.

        This works well with old style classes because they all inherit from 'types.InstanceType',
        but fails to work with new style classes because there is not a single match between an objects
        'type' and a type in the dictionary (since the dictionary contains predefinite keys)

        In order to solve this problem this class overrides this methods and provides a generic hook
        in form of object adaptation to the ITransportedObject protocol.
        If the adaptation fails then the original value is passed to the superclass's implementation.

        The adaptation allows to convert one unsupported type in some supported type.
        A predefined adapter transforms generic objects (those containing a '__dict__' attribute) 
        into dictionaries.

        Custom adapters may perform additional processing, if needed.
        """
        return self._super.__dump(self, adapt(value, ITransportedObject, value), write)

# hack. this is needed because the xmlrpclib.dumps is monolitic and there is no clean hooking of marshallers
import sys
sys.modules['xmlrpclib'].Marshaller = Marshaller
sys.modules['xmlrpclib'].Unmarshaller = Unmarshaller


class ITransportedObject(Interface):
    """
    Interface implemented by those objects who can be passed unchanged through xmlrpc.
    Objects can define custom adapters to this interface in order to be tranportable thorugh xmlrpc.
    """
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/ITransportedObject')])

class INativeTransportedObject(Interface):
    """
    Objects that live on the server side of the xmlrpc implement this interface.
    Special wrapped structures (dicts having special keys) can be adapted to an objects implementing this
    interface using the adapter for the dictionary type
    """
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/INativeTransportedObject')])

class Server(ThreadingMixIn, SimpleXMLRPCServer):
    """
    This is the xmlrpc server.

    It is single threaded

    The xmlrpc methods are implemented in a control object which must be passed to the Server constructor.
    Each method in the control object will be exposed as a method of xmlrpc

    """

    allow_reuse_address = True
    
    # use ThreadLocalClass metaclass
    classThreadLocal = threading.local()

    def __init__(self, port, loglevel, control):
        """
        Constructor. The control should be a subclass of salamoia.h2o.service.Service
        (not enforced) or should implement the _authenticate method.

        TODO: express this enforcement through an interface
        """

        SimpleXMLRPCServer.__init__(self, ('0.0.0.0', port), 
                                    requestHandler = SalamoiaXMLRPCRequestHandler,
                                    logRequests = loglevel)
        self.register_instance(control)

    def _marshaled_dispatch(self, data, dispatch_method = None):
        """
        During this method call the thead local variable "classThreadLocal.service"
        is set to the current service of the invocation, so that adapters lookup 
        service specific type maps    
        """
        self.classThreadLocal.service = self.instance.service()
        try:        
            return SimpleXMLRPCServer._marshaled_dispatch(self, data, dispatch_method)
        finally:
            self.classThreadLocal.service = None

    def _dispatch(self, method, params):
        """
        This method prints any exceptions occoured during the method dispatch
        """

        try:
            return SimpleXMLRPCServer._dispatch(self, method, params)
        except:
            Ione.exception('XMLRPC exception', traceback=True)
            raise

                

    @classmethod
    def adaptObjectToTransportedObject(self, obj):
        """
        uses "inspectableDict" to obtain the attributes that needs to be transported
        and removes special attributes that are not transportable.
        
        The dictionary will present three special attributes:
        
        _type: the type name associated with the object
        _id: the id
        _owner: the id of the owner, or null

        TODO: should recurse
        TODO: refactor this attribute deletion in a 'transportableDict' in salamoia.h2o.Object
        """

        schema = obj._service.serviceDescription.schema
        type_ = schema.reverseClassMap.get(obj.__class__)

        if not type_:
            raise TransformationError, "No registered transformation for %s" % (obj.__class__)
        res = obj.inspectableDict()
        del res['acl']
        res['_type'] = type_
        res['_id'] = obj.id
        res['_owner'] = obj.owner and obj.owner.id

        return res

    @classmethod
    def adaptDictToNativeTransportedObject(cls, obj):
        """
        Create server side objects from a wrapped dictionary.

        If the dictionary contains the '_type' key then it's interpreted as an h2o.Object.
        The newly created object receives the _service attribute and is 'resurrected' (the id will be computed)

        During the adaptation the Service.classThreadLocal.service must point to the current service

        TODO:
        """

        service = cls.classThreadLocal.service
        schema = service.serviceDescription.schema
        type_ = obj.get('_type')
        if type_:
            res = schema.classMap[type_]()
            for k in obj.keys():
                setattr(res, k, obj[k])
            # do additional post transmit steps
            res._service = service        
            ownerID = obj.get('_owner')
            if ownerID:
                res.owner = service.fetch(ownerID)
            res.resurrect()
            return res

        return obj

            
    def serv(self):
        """
        Traps keyboard interrupt
        """
        try:
            self.serve_forever()
        except SystemExit:
            print "\nExiting"
            pass
        except KeyboardInterrupt:
            print "\nInterrupted"
            pass

class SalamoiaXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """
    This is a special request handler that hooks the POST handler in order to add http basic authentication
    """

    def do_POST(self):
        """
        Gets the authentication headers from the request and processes them calling the _authenticate method
        in the control instance.

        Sets the 'path' instance variable of the Server to the request path. (caution with threads)
        """

        self.server.instance.threadLocal.path = self.path

        auth = self.headers.get('authorization')
        if not auth:
            return self.unauthenticated()

        principal = None
        
        authType, credentials = auth.split(' ')
        
        if authType == "Basic":
            user, password = base64.decodestring(credentials).split(':')
            principal = Principal(user, password, self.server.instance.service())
        elif authType == "Token":
            principal = Principal.fromToken(credentials, self.server.instance.service())
        else:
            Ione.error("unknown authentication type", authType)
            return self.unauthenticated()

        if principal and (adapt(principal, IAuthenticatedPrincipal, False) or self.server.instance._authenticate(principal)):
            self.server.instance.service()._authenticated(principal)
            return SimpleXMLRPCRequestHandler.do_POST(self)

        return self.unauthenticated()

    def unauthenticated(self):
        """
        Informs the browser that an error occoured during authentication
        """

        service = self.server.instance.service()
        
        realm = service.servicePath[1:] # strip the leading /
        challenge = service.proxy("/authmanager").challenge('*')

        sshAuthHeader = 'SSH realm="%s",challenge="%s"' % (realm, challenge)
        basicAuthHeader = 'Basic realm="%s"' % (realm)
        
        self.send_response(401)
        self.send_header("WWW-Authenticate", basicAuthHeader)
        self.send_header("WWW-Authenticate", sshAuthHeader)
        self.end_headers()
        # eat arguments, avoid broken pipe error
        #self.rfile.read(int(self.headers["content-length"]))


# from objects to dicts
def newStyleObjectTransportableAdapter(self):
    """
    This adapter transform new-style instances into attribute dicionaries.
    Using this adapter you can transport new-style instances transparently though 
    the xmlrpc marshaller
    """
    if hasattr(self, '__dict__'):
        return self.__dict__

declareAdapter(newStyleObjectTransportableAdapter, [ITransportedObject], forTypes=[object])
declareAdapter(Server.adaptObjectToTransportedObject, [ITransportedObject], forProtocols=[IObject])

# from dicts to objects
declareAdapter(Server.adaptDictToNativeTransportedObject, [INativeTransportedObject], forTypes=[dict])

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
