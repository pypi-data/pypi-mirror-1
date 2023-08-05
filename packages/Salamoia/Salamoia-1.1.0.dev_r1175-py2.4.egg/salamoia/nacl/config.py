import salamoia.h2o.config
import os

class Config(salamoia.h2o.config.Config):
    def defaultFilenames(self):
        return ['~/.naclrc','/etc/salamoia/nacl.conf']

