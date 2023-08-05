from salamoia.macina.backend import *
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *


class SlaveBackend(MacinaBackend):

    def controlClass(self):
        return SlaveBackendModularControl



class SlaveBackendControl(BackendControl):
    
    def __init__(self):
        super(SlaveBackendControl, self).__init__()


    def checkCredentials(self, user, password, uri=None):
        """
        Check the credentials trying to connect to the Slave directory
        binding as the user.
        """
        
        Ione.log("Checking credentials ... takes time", level=LOG_WARNING)
                
    def test(self, arg):
        print "Slave TESTING", arg
        print arg
        return arg

# hack
class SlaveBackendModularControl(BackendMixin, 
                                SlaveBackendControl):
    pass

Backend.registerBackend("slave", SlaveBackend)
