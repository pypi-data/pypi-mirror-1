from salamoia.h2o.exception import *
from salamoia.h2o.bundlemanager import BundleManager
from salamoia.h2o.service import Service

import threading

__all__ = ['ServiceDispatcher']

class ServiceDispatcher(object):
    """
    The service dispatcher is the first responder of the xml server.
    It dispatches to the correct Service depending on the "path"
    """
    
    def __init__(self):
        super(ServiceDispatcher, self).__init__()

        self.services = {}
        self.threadLocal = threading.local()

    def register(self, service):
        """
        Services are registered with this methods.

        A registered service is reachable through this dispatcher using it's `serviceName`
        """

        self.services[service.serviceName] = service

    def _dispatch(self, method, args):
        """
        Invokes the method in the current service
        """

        service = self.service()
        if hasattr(service, method):
            m = getattr(service, method)
            return m(*args)

        raise ServiceDoesNotImplementException, "method not found %s" % (self.method)


    def _authenticate(self, user, password):
        """
        Forwards the authentication to the current service
        """
        return self.service()._authenticate(user, password)

    def service(self):
        """
        Gets the current service from the request path.

        If it cannot find the registered service it triggers a refresh in the bundle manager
        and tries again once. If the problem is not fixed it raises an error.
        """
        try:
            return self.services[self.threadLocal.path.split('/')[1]]
        except KeyError:
            BundleManager.defaultManager().refresh()
            try:
                return self.services[self.threadLocal.path.split('/')[1]]
            except KeyError:
                raise ServiceNotFoundException, "service %s (uri %s)" % (self.threadLocal.path.split('/')[1], self.threadLocal.path)
    
