from salamoia.h2o.logioni import Ione
from salamoia.h2o.xmlparser import Element
from salamoia.h2o.bundle import Description

from salamoia.h2o.dottedname import resolve
from salamoia.h2o.decorators.lazy import *

from salamoia.h2o.schemamanager import SchemaManager

import sys

__all__ = ['Service', 'ServiceDescription']

class Service(object):
    """
    Control objects are used to provide methods to xmlrpc servers.

    Usually backends have subclasses of this one providing the methods to export

    The minimum interface is the _authenticate method used in xmlserver.Server
    """

    def registerDescription(self, description):
        """
        This is something similar to a constructor but allows the main constructor to be parametereless.
        
        Used to construct a service from a ServiceDescription. Basically it just initializes the `serviceName`
        and `serviceDescription` instance variables. `serviceName` will be used when registering the service
        to the ServiceDispatcher. The `serviceDescription` is useful to get all other parameters, like the schema etc.

        """
        self.serviceName = description.name
        self.serviceDescription = description

    def _authenticate(self, username, password, uri=None):
        self._currentUser = username
        return True

    def reloadBundle(self):
        """
        Reloads the module where the current service is defined.
        Doesn't reload superclasses.
        """
        reloaded = reload(sys.modules[self.__module__])
        self.__class__ = getattr(reloaded, type(self).__name__)

        Ione.log("reloaded service", self)


###

class HandlerElement(Element):
    childClasses = {}
    attributes = ['class', 'schema']

    def init(self):
        super(HandlerElement, self).init()

        # 'class' is a python reserved word
        self.className = self.getAttribute('class')


class ServiceDescription(Description):
    """
    A service description is an XML tree describing a service.
    Currently the only informations provided are the dotted path to the python class implementing the service
    (for example salamoia.nacl.ldap.ldapbackend.Service) and the name of the associated schema.
    
    TODO: please abstract the "schema" thing. only some services have the notion of schemas at all
    """

    childClasses = {'handler': HandlerElement}
    attributes = ['name', 'container']

    dtd = 'service.dtd'
    rootElementName = "service"

    def __repr__(self):
        return "<ServiceDescription %s>" % (self.name)

    def init(self):
        super(ServiceDescription, self).init()

        self.handler = self.findChild(HandlerElement)

    @lazy
    def schema(self):
        schemaName = self.handler.schema
        return SchemaManager.defaultManager().schemaNamed(schemaName)

    def activate(self):
        """
        Called when the Bundle is activated.

        Instantiates the service class provided by the user and register it to the service dispatcher
        """

        from salamoia.h2o.backend import Backend
        backend = Backend.defaultBackend()

        super(ServiceDescription, self).activate()
        
        serviceClass = resolve(self.handler.className)
        service = serviceClass()
        service.registerDescription(self)

        backend.serviceDispatcher.register(service)

        
    
