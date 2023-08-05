import salamoia.h2o.config
import os
from salamoia.h2o.pathelp import *

hasGeneratedConfig = False
try:
    import frontends.generated_config
    hasGeneratedConfig = True
except:
    pass

class Config(salamoia.h2o.config.Config):
    def defaultFilenames(self):
        return ['~/.salamoiarc','/etc/salamoia/salamoia.conf']

    def profileSection(self):
        return "Connection"

    def libdir(self):
        if hasGeneratedConfig:
            return path(frontends.generated_config.libdir) 
        #return path(frontends.__path__[0]) / "oliva" / "lib"
        return None
        #return path(")
    
