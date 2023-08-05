from salamoia.macina.backend import *
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *


class MasterBackend(MacinaBackend):

    def controlClass(self):
        return MasterBackendModularControl



class MasterBackendControl(BackendControl):
    
    def __init__(self):
        super(MasterBackendControl, self).__init__()


    def checkCredentials(self, user, password, uri=None):
        """
        Check the credentials trying to connect to the Master directory
        binding as the user.
        """
        
        Ione.log("Checking credentials ... takes time", level=LOG_WARNING)
                
    def test(self, arg):
        print "Master TESTING", arg
        print arg
        return arg

# hack
class MasterBackendModularControl(BackendMixin, 
                                MasterBackendControl):
    pass

Backend.registerBackend("master", MasterBackend)
