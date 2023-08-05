import salamoia.h2o.config
import os

hasGeneratedConfig = False
try:
    import frontends.generated_config
    hasGeneratedConfig = True
except:
    pass

class Config(salamoia.h2o.config.Config):
    def defaultFilenames(self):
        return [ '/etc/salamoia/salamoia.conf', os.path.expanduser('~/.salamoiarc')]

    def profileSection(self):
        return "Connection"

    def libdir(self):
        return self.getpath('oliva', 'installdir')

    
