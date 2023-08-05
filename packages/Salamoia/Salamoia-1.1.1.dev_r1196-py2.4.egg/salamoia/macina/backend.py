from salamoia.h2o.xmlcontrol import *
from salamoia.h2o.xmlserver  import *
from salamoia.h2o.reflection import *
from salamoia.h2o.acl        import *
from salamoia.h2o.exception  import *
from salamoia.h2o.daemonizer import *
from salamoia.h2o.logioni    import *
from salamoia.h2o.container  import *
from salamoia.h2o.object     import *
from salamoia.macina.config    import Config

from salamoia.h2o.backend import Backend

from optparse import OptionParser
from salamoia.h2o.feedcollection import * 
import time
import os
# from salamoia.macina.backendmixin import * look to the bottom

class MacinaBackend(Backend):

    name = "nacl"

    configClass = Config

    def controlClass(self):
        """
        Return the controller class.
        Subclasses may create their own controller and override this method
        in order to return that class.
        """
        return BackendModularControl

    def installationPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "installationPath", "/usr/local/salamoia/development")

    def scriptPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "scriptsPath", 
                       os.path.join(self.installationPath(), "scripts"))

    def rootPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "rootPath", "")

    def varPath(self):
        cfg = Config()
        return cfg.get(self.defaultProfile(), "varPath", "/var/lib/salamoia")

from salamoia.macina.backendmixin import *

            
class BackendControl(Control):
    """
    This class implements the XMLRPC server methods exported through the
    Backend server.

    Normally they provide some logging and general actions but most of
    the intelligence is in the objects themselves.

    Please add non basic functionality in BackendMixin superclasses
    (see backendmixin.py)
    """
    
    usage = "Backend Function"
    def __init__(self):
        #print "Backend mro", self.__class__.mro()
        super(BackendControl, self).__init__()
        self.usage = self.__class__.usage
        self.startupTime = time.time()	
	




class BackendModularControl(BackendMixin, BackendControl):
    def __init__(self):
        super(BackendModularControl, self).__init__()

from slave.slavebackend import SlaveBackend
from master.masterbackend import MasterBackend


