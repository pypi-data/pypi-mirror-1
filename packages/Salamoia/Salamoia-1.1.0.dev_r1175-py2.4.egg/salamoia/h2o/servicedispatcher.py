class ServiceDispatcher(object):
    """
    The service dispatcher is the first responder of the xml server.
    It dispatches to the correct Service depending on the "path"
    """
    
    def __init__(self):
        self.services = {}

    def register(self, service):
        self.services[service.serviceName] = service

    def _dispatch(self, method, args):
        """
        Invokes the method in the current service
        """
        
        #print "DISPATCHING", self.path, self.service(), method, args

        service = self.service()
        if hasattr(service, method):
            m = getattr(service, method)
            return m(*args)

        raise "DOES NOT IMPLEMENT"


    def _authenticate(self, user, password):
        """
        Forwards the authentication to the current service
        """
        return self.service()._authenticate(user, password)

    def service(self):
        """
        Gets the current service from the request path
        """
        return self.services[self.path.split('/')[1]]
    
