from salamoia.h2o.xmlparser import Element, RootElement

class Service(object):
    """
    Control objects are used to provide methods to xmlrpc servers.

    Usually backends have subclasses of this one providing the methods to export

    The minimum interface is the _authenticate method used in xmlserver.Server
    """

    def _authenticate(self, username, password, uri=None):
        self._currentUser = username
        return True


###

class ServiceDescription(RootElement):
    childClasses = {}
    attributes = ['name']

    dtd = 'service.dtd'
    rootElementName = "service"
    validable = False
    
