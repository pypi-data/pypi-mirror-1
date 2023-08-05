from salamoia.h2o.decorators import lazymethod
from salamoia.h2o.logioni import Ione
from ConfigParser import ConfigParser, Error as ConfigKeyError
import os

from salamoia.utility.pathelp import path

__all__ = ['Config']

class Config(ConfigParser):
    """
    This class implements a handy configuration parser based
    on ConfigParser, but it can be reimplemented maintaining the
    basic interface 'get' and 'getint'

    TODO: implement 'python' configuration files, executing python
    code ....
    """
    
    _filenames = None
    
    def __init__(self):
        ConfigParser.__init__(self)
        self.read()

    @staticmethod
    def defaultFilenames():
        """
        return a list of filenames
        """
        from salamoia.h2o.backend import Backend
        return [os.path.expanduser(x) for x in Backend.defaultBackend().configFilenames()]
        
    def quickRead(self, paths=None):
        if not paths:
            paths = self.filenames()
            self.paths = paths

        ConfigParser.read(self, paths)

    def read(self, paths=None):
        self.quickRead(paths)

        def override(p):
            cfg = ConfigParser()
            cfg.read(p)
            try:
                over = cfg.get('general', 'overrides')
                return [p] + override(over)
            except ConfigKeyError:
                return [p]
        
        over = None
        for p in list(self.paths):
            cfg = ConfigParser()
            cfg.read(p)
            try:
                over = cfg.get('general', 'overrides')
                inserted = override(over)
                pos = self.paths.index(p)
                for i in inserted:
                    self.paths.insert(pos, i)

            except ConfigKeyError:
                pass

        if over:
            Ione.log("Configuration paths:", self.paths)
            #self.clear()
            ConfigParser.read(self, self.paths)


    def clear(self):
        for s in self.sections():
            self.remove_section(s)

    def get(self, section, option, default=''):
        """
        wraps ConfigParser.get() returning the default
        if there is no key
        """

        try:
            return ConfigParser.get(self, section, option)
        except ConfigKeyError:
            return default

    def getint(self, section, option, default=0):
        """
        transforms the result to an integer
        """
        try:
            res =  ConfigParser.get(self, section, option)
            return int(res)
        except ConfigKeyError:
            return default

    def getboolean(self, section, option, default=False):
        """
        transforms the result to an integer
        """
        def booleanize(res):
            if not isinstance(res, basestring):
                return res
            if res.lower() in ('yes', 'true', 'on'):
                return True
            if res.lower() in ('no', 'false', 'off'):
                return False
            raise TypeError, "not valid boolean"
            
        try:
            res = ConfigParser.get(self, section, option)
            return booleanize(res)
        except ConfigKeyError:
            return booleanize(default)

    def getpath(self, section, option, default=''):
        """
        trasform result into a path
        """
        return path(self.get(section, option, default))

    def getpaths(self, section, option, default=''):
        """
        trasform result p1:p2:...:pn into a list of paths 
        """
        return [path(x) for x in self.get(section, option, default).split(':')]

    @classmethod
    def setConfigFiles(cls, filenames):
        """
        
        """
        cls._filenames = filenames

    @classmethod
    def setConfigFile(cls, filename):
        """
        Called from backend command line parsing
        """
        cls.setConfigFiles([filename])
        
    
    def filenames(self):
        """
        if not set with setConfigFile() the config filename
        defaults to what defaultFilename() returns
        """
        if not self._filenames:
            self._filenames = self.defaultFilenames()
        return self._filenames

    _defaultConfig = {}

    @classmethod
    @lazymethod
    def defaultConfig(cls):
        return cls()

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
