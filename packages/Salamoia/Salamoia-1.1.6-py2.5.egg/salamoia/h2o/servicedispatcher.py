from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import ServiceDoesNotImplementException, ServiceNotFoundException
from salamoia.h2o.bundlemanager import BundleManager
from salamoia.h2o.service import Service
from salamoia.h2o.functional import partialProperty

import threading

__all__ = ['ServiceDispatcher']

class RootService(Service):
    """
    The root service is a service that provides minimal introspection methods.
    It is bound to the root of the path and delegates methods to its children
    """

class ServiceDispatcher(object):
    """
    The service dispatcher is the first responder of the xml server.
    It dispatches to the correct Service depending on the "path"
    """
    
    def __init__(self):
        super(ServiceDispatcher, self).__init__()

        self.rootService = RootService()
        self.threadLocal = threading.local()

    @partialProperty(lambda self: self.threadLocal.path)
    def path(self, val):
        self.threadLocal.path = val

    def register(self, service):
        """
        Services are registered with this methods.

        A registered service is reachable through this dispatcher by traversing the rootService.

        Each service has a dictionary mapping names to subcomponents (see Service._registerSubcomponent)
        Registration works by traversing through the parent of the to-be-registered object and registering
        directly with them. Custom implementation of Service may override both _registerSubcomponent and _traverse.
        
        """

        name = service.serviceName
        if not name.startswith('/'):
            name = '/' + name

        components = name.split('/')[1:-1]
        base = self.rootService._traverse(components)
        
        base._registerSubcomponent(service.serviceName.split('/')[-1], service)
        service._parent = base


    def _dispatch(self, method, args):
        """
        Invokes the method in the current service
        """

        service = self.service()
        if hasattr(service, method):
            m = getattr(service, method)
            return m(*args)

        raise ServiceDoesNotImplementException, "method not found %s" % (method)


    def _authenticate(self, principal):
        """
        Forwards the authentication to the current service
        """
        return self.service()._authenticate(principal)

    def service(self):
        """
        Gets the current service from the request path.

        If it cannot find the registered service it triggers a refresh in the bundle manager
        and tries again once. If the problem is not fixed it raises an error.
        """
        try:
            return self._service()
        except ServiceNotFoundException:
            BundleManager.defaultManager().refresh()
            try:
                return self._service()
            except ServiceNotFoundException:
                raise ServiceNotFoundException, "service %s (uri %s)" % (self.threadLocal.path.split('/')[-1], self.threadLocal.path)
    
    def _service(self):
        components = self.threadLocal.path.split('/')[1:]
        return self.rootService._traverse(components)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
