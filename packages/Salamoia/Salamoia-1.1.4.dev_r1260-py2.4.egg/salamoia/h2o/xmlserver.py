import xmlrpclib

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import base64

from salamoia.h2o.object import Object, IObject
from salamoia.h2o.exception import TransformationError
from salamoia.h2o.auth import Principal

import threading
import sys, traceback

from protocols import declareAdapter, declareImplementation, protocolForURI, Interface, advise, sequenceOf, NO_ADAPTER_NEEDED
types = __import__('types')

__all__ = ['Server']


class ITransportedObject(Interface):
    """
    Interface implemented by those objects who can be passed unchanged through xmlrpc.
    Objects that are not supported by xmlrpc can be define an adaptor to this interface and they'll 
    become transportable.
    """
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/ITransportedObject')])

class IListOfTransportedObjects(Interface):
    """
    A list of transportable objects.
    It automatically registers an adapter that adapts ITransportedObject over each element of an IBasicSequence
    (list, tuple, and generator (this one added in salamoia/__init__.py. perhaps in future releases of PyProtocols))

    This approach is more elegant than having seprate adapters for each kind of sequence 
    but has the disadvantage that tuples are converted to lists. 
    (However it is a good example of the power of adapters, imagine all the isinstance checks otherwise..)
    """
    advise(protocolExtends=[ITransportedObject],
           equivalentProtocols=[sequenceOf(ITransportedObject)])

class INativeTransportedObject(Interface):
    """
    Objects that live on the server side of the xmlrpc implement this interface.
    Special wrapped structures (dicts having special keys) can be adapted to an objects implementing this
    interface using the adapter for the dictionary type
    """
    advise(equivalentProtocols=[protocolForURI('http://interfaces.salamoia.org/INativeTransportedObject')])

class IListOfNativeTransportedObjects(Interface):
    advise(protocolExtends=[INativeTransportedObject],
          equivalentProtocols=[sequenceOf(INativeTransportedObject)])


class Server(ThreadingMixIn, SimpleXMLRPCServer):
    """
    This is the xmlrpc server.

    It is single threaded

    The xmlrpc methods are implemented in a control object which must be passed to the Server constructor.
    Each method in the control object will be exposed as a method of xmlrpc

    """

    allow_reuse_address = True
    
    classThreadLocal = threading.local()

    def __init__(self, port, loglevel, control):
        """
        Constructor. The control should be a subclass of salamoia.h2o.xmlcontrol.Control (not enforced) or should implement the _authenticate method
        """

        SimpleXMLRPCServer.__init__(self, ('0.0.0.0', port), 
                                    requestHandler = SalamoiaXMLRPCRequestHandler,
                                    logRequests = loglevel)
        self.register_instance(control)

    def _marshaled_dispatch(self, data, dispatch_method = None):
        """
        Brutto ma necessario per gestire il None, perche i maledetti usano una funzione
        chiamata "xmlrpclib.dumps" che non si puo' overraidare e che ha un bellissimo default
        allow_none=0, quindi non ci resta che copiaincollare questo metodo e cambiarne l'implementazione

        It also extends the SimpleXMLRPCServer outputing optionally the backtrace on the server side
        """
        params, method = xmlrpclib.loads(data)
        # generate response
        try:
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1, allow_none=True)
        except xmlrpclib.Fault, fault:
            if True:
                traceback.print_tb(sys.exc_info()[2])
            response = xmlrpclib.dumps(fault)
        except:
            # report exception back to server
            if True:
                traceback.print_tb(sys.exc_info()[2])
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s" % (sys.exc_type, sys.exc_value))
                )
                
        return response        

    def _dispatch(self, method, params):
        """
        Transform the parameters and the return value using adapters for the interface ITransportedObject and INativeTransportedObject
        """
        self.classThreadLocal.service = self.instance.service()
        try:
            cparams = INativeTransportedObject(params)
            res = SimpleXMLRPCServer._dispatch(self, method, cparams)
        finally:
            self.classThreadLocal.service = None
        return ITransportedObject(res)

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

        authType, credentials = auth.split(' ')
        if authType != "Basic":
            return self.unauthenticated()

        user, password = base64.decodestring(credentials).split(':')

        principal = Principal(user, password, self.server.instance.service())

        if self.server.instance._authenticate(principal):
            return SimpleXMLRPCRequestHandler.do_POST(self)

        return self.unauthenticated()

    def unauthenticated(self):
        """
        Informs the browser that an error occoured during authentication
        """

        self.send_response(401)
        self.end_headers()
        # eat arguments, avoid broken pipe error
        self.rfile.read(int(self.headers["content-length"]))


nativeTransportableTypes = [basestring, int, dict, types.NoneType]

# from objects to dicts
declareAdapter(NO_ADAPTER_NEEDED, [ITransportedObject], forTypes=nativeTransportableTypes)
declareAdapter(Server.adaptObjectToTransportedObject, [ITransportedObject], forProtocols=[IObject])

# from dicts to objects
declareAdapter(NO_ADAPTER_NEEDED, [ITransportedObject], forTypes=nativeTransportableTypes)
declareAdapter(NO_ADAPTER_NEEDED, [INativeTransportedObject], forProtocols=[ITransportedObject])
declareAdapter(Server.adaptDictToNativeTransportedObject, [INativeTransportedObject], forTypes=[dict])

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
