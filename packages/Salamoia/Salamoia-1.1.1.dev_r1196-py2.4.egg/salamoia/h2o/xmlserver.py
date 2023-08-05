import xmlrpclib
from xmlrpclib import Fault

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import base64

from salamoia.h2o.object import Object

import sys, pdb, traceback

__all__ = ['Server']

class Server(ThreadingMixIn, SimpleXMLRPCServer):
    """
    This is the xmlrpc server.

    It is single threaded

    The xmlrpc methods are implemented in a control object which must be passed to the Server constructor.
    Each method in the control object will be exposed as a method of xmlrpc

    """

    allow_reuse_address = True

    def __init__(self, port, loglevel, control):
        """
        Constructor. The control should be a subclass of salamoia.h2o.xmlcontrol.Control (not enforced) or should implement the _authenticate method
        """

        SimpleXMLRPCServer.__init__(self, ('localhost', port), 
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
        except Fault, fault:
            if True:
                traceback.print_tb(sys.exc_traceback)
            response = xmlrpclib.dumps(fault)
        except:
            # report exception back to server
            if True:
                traceback.print_tb(sys.exc_traceback)
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s" % (sys.exc_type, sys.exc_value))
                )
                
        return response

    def _dispatch(self, method, params):
        """
        Transform the parameters and the return value using respectively
        transformObjectToDict and transformDictToObject
        """
        cparams = [self.transformDictToObject(x) for x in params]
        res = SimpleXMLRPCServer._dispatch(self, method, cparams)

        return self.transformObjectToDict(res)

    def transformDictToObject(self, obj):
        """
        If a dictionary has a special '_type' key then 
        a class is looked up in the service schema's classMap attribute, instantiated and populated
        with the attributes.

        Then it's resurrect method is called, so that it can do post transform custom adjustment

        If the argument is a list then does the same thing but on each element of the list

        TODO: should recurse
        """
        if isinstance(obj, list):
            return [self.transformDictToObject(x) for x in obj]

        if isinstance(obj, dict):
            schema = self.instance.service()
            type = obj.get('_type')
            if type:
                res = schema.classMap[type]()
                for k in obj.keys():
                    setattr(res, k, obj[k])
                # do additional post transmit steps
                res.resurrect()
                return res
        return obj
                

    def transformObjectToDict(self, obj):
        """
        inverse of transofrmDictToObject

        uses "inspectableDict" to obtain the attributes that needs to be transported
        and removes special attributes that are not transportable.
        
        The dictionary will present three special attributes:
        
        _type: the type name associated with the object
        _id: the id
        _owner: the id of the owner, or null

        TODO: should recurse
        TODO: refactor this attribute deletion in a 'transportableDict' in salamoia.h2o.Object
        """
        if isinstance(obj, list):
            return [self.transformObjectToDict(x) for x in obj]

        if isinstance(obj, Object):
            schema = obj._service.serviceDescription.schema
            type = schema.reverseClassMap.get(obj.__class__)

            if not type:
                raise "Error", "No registered transformation for %s" % (obj.__class__)
            res = obj.inspectableDict()
            del res['acl']
            res['_type'] = type
            res['_id'] = obj.id
            res['_owner'] = obj.owner and obj.owner.id

            return res
        return obj
            
            
    def serv(self):
        """
        Traps keyboard interrupt
        """
        try:
            self.serve_forever()
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

        if self.server.instance._authenticate(user, password):        
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
