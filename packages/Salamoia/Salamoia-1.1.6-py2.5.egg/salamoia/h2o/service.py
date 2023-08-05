from salamoia.h2o.logioni import Ione
from salamoia.h2o.xmlparser import Element
from salamoia.h2o.bundle import Description

from salamoia.h2o.dottedname import resolve
from salamoia.h2o.decorators import lazy

from salamoia.h2o.schema import Schema, ISchema
from salamoia.h2o.schemamanager import SchemaManager
from salamoia.h2o.exception import ServiceNotFoundException
from salamoia.h2o.protocols import Interface, advise, protocolForURI, declareAdapter, Attribute

from salamoia.h2o.functional import AttributeAccessor, instancesOf
from salamoia.utility.pathelp import path as Path

import sys

__all__ = ['Service', 'ServiceDescription']

class IService(Interface):
    advise(equivalentProtocols=[protocolForURI("http://interfaces.salamoia.org/IService")])

    serviceDescription = Attribute('reference to the ServiceDescription object')

declareAdapter(AttributeAccessor.serviceDescription.schema, [ISchema], forProtocols=[IService])

class Service(object):
    """
    Control objects are used to provide methods to xmlrpc servers.

    Usually backends have subclasses of this one providing the methods to export

    The minimum interface is the _authenticate method used in xmlserver.Server

    A Service implements the IService interface::

        >>> s = Service()
        >>> IService(s) is s
        True
    
    """

    advise(instancesProvide=[IService])

    def __init__(self):
        """
        Constructs a service.

        ---- private doc

        A new service has no parent:
        >>> Service()._parent is None
        True

        and no subcomponents:
        >>> Service()._subcomponents
        {}
        """

        super(Service, self).__init__()

        self._subcomponents = {}
        self._parent = None

    def registerDescription(self, description):
        """
        This is something similar to a constructor but allows the main constructor to be parametereless.
        
        Used to construct a service from a ServiceDescription. Basically it just initializes the `serviceName`
        and `serviceDescription` instance variables. `serviceName` will be used when registering the service
        to the ServiceDispatcher. The `serviceDescription` is useful to get all other parameters, like the schema etc.

        >>> service = '''<service name="test">\
          <handler class="salamoia.nacl.ldap.service.Service" schema="test"/>\
          <subservice name="subtest">\
            <handler class="Metadata::metadata.Metadata"/>\
          </subservice>\
        </service>\
        '''
        >>> from salamoia.h2o.bundle import StringWrapper
        >>> sd = ServiceDescription(StringWrapper(service))
        >>> sd.name
        u'test'
        >>> len(sd.subservices)
        1
        >>> sd.subservices[0].handler.className
        u'Metadata::metadata.Metadata'
        
        """
        self.serviceName = description.name
        self.serviceDescription = description
        description.service = self

    def schemaClass(self):
        """
        You can override this in your subclasses
        """
        return Schema

    def _authenticated(self, principal):
        """
        called when the service is authenticated to a principal (at every request)

        TODO: threadsafe
        """
        self._currentPrincipal = principal

        # will be obsoleted
        self._currentUser = principal.username

    def _authenticate(self, principal, uri=None):
        """
        Returns true if it accepts credentials.

        The default implementation authenticates with the parent service.

        Usually the overriden methods will not call this implementation
        """
        if self._parent:
            return self._parent._authenticate(principal)
        return False

    def _registerSubcomponent(self, name, service):
        """
        Register sub service 
        """
        self._subcomponents[name] = service
    
    def _traverse(self, components):
        """
        """
        if len(components) == 0:
            return self

        if not components[0]:
            def findRoot(service):
                if service._parent:
                    return findRoot(service._parent)
                return service
            return findRoot(self)._traverse(components[1:])

        if components[0] == "..":
            return self._parent._traverse(components[1:])

        if self._subcomponents.has_key(components[0]):
            sub = self._subcomponents[components[0]]
            if len(components) == 1:
                return sub
            return sub._traverse(components[1:])
        raise ServiceNotFoundException, "service %s (relative uri %s)" % (self, components)

    def reloadBundle(self):
        """
        Reloads the module where the current service is defined.
        Doesn't reload superclasses.
        """
        reloaded = reload(sys.modules[self.__module__])
        self.__class__ = getattr(reloaded, type(self).__name__)

        Ione.log("reloaded service", self)

    def proxy(self, path):
        """
        returns a proxy for another service given a (relative) path.

        The path may contain also '..' for going back to parent

        it's intended to be called locally from other services
        """

        return self._traverse(path.split('/'))

    @property
    def servicePath(self):
        """
        Returns the absolute path of this service
        """
        if not self._parent:
            return ""
        
        return '/'.join((self._parent.servicePath, self.serviceName))

    def connectionAuthenticationCheck(self):
        """
        This method is used to test the connection to this service.

        Authentication negotiation uses this method.
        """
        return True

    def whoAmI(self, *args):
        """
        debugging method, remove me
        """
        return self._currentPrincipal.username

###

class HandlerElement(Element):
    """
    TODO: please abstract the "schema" thing. only some services have the notion of schemas at all
    """
    
    childClasses = {}
    attributes = ['class', 'schema']

    def init(self):
        super(HandlerElement, self).init()

        # 'class' is a python reserved word
        self.className = self.getAttribute('class')

    def handlerClass(self):
        """
        Return the handler class resolved as a dotted name (salamoia.h2o.dottedname)

        Relative names are resolved relative to the module of xml file describing this element.
        
        The module of the xml file is calculated using it's file path converted in dotted notation, so it may
        not be correcy. 

        TODO: fix this, adding the notion of root element module to the xmlparser

        >>> service = '''
        ... <service name="handlerTest">
        ...   <handler class=".somemodule.SomeClass" schema="test"/>
        ... </service>
        ... '''
        >>> from salamoia.h2o.bundle import StringWrapper
        >>> file = StringWrapper(service)
        >>> file.path = "test/somewhere/somewhere.xml"
        >>> sd = ServiceDescription(file)
        >>> sd.name
        u'handlerTest'

        >>> c = sd.handler.handlerClass()
        Traceback (most recent call last):
        ...
        ImportError: No module named somewhere
        
        """
        module = Path(self.filename()[:-1]).replace('/','.')
        return resolve(self.className, module)

class MixinElement(Element):
    """
    """
    
    childClasses = {}
    attributes = ['class']

    def init(self):
        super(MixinElement, self).init()

        # 'class' is a python reserved word
        self.className = self.getAttribute('class')

    def mixinClass(self):
        module = Path(self.filename()[:-1]).replace('/','.')
        return resolve(self.className, module)

class SubServiceElement(Element):
    childClasses = {'handler': HandlerElement}
    attributes = ['name']

    def init(self):
        super(SubServiceElement, self).init()

        self.handler = self.findChild(HandlerElement)
        self.subservices = instancesOf(SubServiceElement, self.children)
        self.service = None

class ServiceDescription(Description):
    """
    A service description is an XML tree describing a service.
    Currently the only informations provided are the dotted path to the python class implementing the service
    (for example salamoia.nacl.ldap.ldapbackend.Service) and the name of the associated schema.

    TODO: please abstract the "schema" thing. only some services have the notion of schemas at all
    """

    childClasses = {'handler': HandlerElement,
                    'subservice': SubServiceElement,
                    'mixin': MixinElement}
    attributes = ['name', 'container']

    dtd = 'service.dtd'
    rootElementName = "service"

    def __repr__(self):
        return "<ServiceDescription %s>" % (self.name)

    def init(self):
        super(ServiceDescription, self).init()

        self.handler = self.findChild(HandlerElement)
        self.subservices = instancesOf(SubServiceElement, self.children)
        self.service = None

    @lazy
    def schema(self):
        """
        Get the schema object from the names found in the 'schema' attribute 

        The schema list is merged together to produce a single schema object.
        """
        manager = SchemaManager.defaultManager()
        return self.service.schemaClass().mergeFrom([manager.schemaDescriptionNamed(x) for x in self.schemaNames()])

    def schemaNames(self):
        """
        The schema attribute is interpreted as a comma separated list of names
        """
        return [x.strip() for x in self.handler.schema.split(',')]

    def activate(self):
        """
        Called when the Bundle is activated.

        Instantiates the service class provided by the user and register it to the service dispatcher
        """

        from salamoia.h2o.backend import Backend
        backend = Backend.defaultBackend()

        super(ServiceDescription, self).activate()
        
        serviceClass = self.handler.handlerClass()
        service = serviceClass()
        service.registerDescription(self)

        backend.serviceDispatcher.register(service)

        # recurse

        for i in self.subservices:
            Ione.log("ACTIVATING SUBSERVICE", i.handler.className)
    

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
