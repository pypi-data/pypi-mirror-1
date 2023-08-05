from ConfigParser import ConfigParser
import os

from pathelp import *

class Config(ConfigParser):
    """
    This class implements a handy configuration parser based
    on ConfigParser, but it can be reimplemented maintaining the
    basic interface 'get' and 'getint'

    TODO: implement 'python' configuration files, executing python
    code ....
    """
    
    _filename = None
    
    def __init__(self):
        ConfigParser.__init__(self)
        self.read()

    def defaultFilename(self):
        """
        return the default filename for the config file.
        If you want to support a single file ovverride this. Otherwise ovverride
        default filenames
        """
        filenames = [x for x in [os.path.expanduser(y) for y in self.defaultFilenames()] if os.path.exists(x)]
        if not filenames:
            raise IOError, "Cannot find configuration files"
        return filenames[0]

    def defaultFilenames(self):
        """
        return a list of filenames
        """
        raise NotImplementedError, "to be overriden"

    def profileSection(self):
        return "General"
        
    def read(self, path=None):
        if not path:
            path = self.filename()
        ConfigParser.read(self, path)

    def get(self, section, option, default=''):
        """
        wraps ConfigParser.get() returning the default
        if there is no key
        """
        try:
            return ConfigParser.get(self, section, option)
        except:
            return default

    def getint(self, section, option, default=0):
        """
        transforms the result to an integer
        """
        try:
            res =  ConfigParser.get(self, section, option)
            return int(res)
        except:
            return default

    def getboolean(self, section, option, default=False):
        """
        transforms the result to an integer
        """
        try:
            res =  ConfigParser.getboolean(self, section, option)
            return res
        except:
            return default

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
    def setConfigFile(cls, filename):
        """
        
        """
        cls._filename = filename
    
    def filename(self):
        """
        if not set with setConfigFile() the config filename
        defaults to what defaultFilename() returns
        """
        if not self._filename:
            self._filename = self.defaultFilename()
        return self._filename

    _defaultConfig = {}
    _defaultProfile = None

    @classmethod
    def defaultConfig(cls, profile=None):
        if not cls._defaultProfile:
            cfg = cls()
            cls._defaultProfile = cfg.get(cfg.profileSection(), 'profile', 'DefaultProfile')
            
        if not profile:
            profile = cls._defaultProfile
            
        if not cls._defaultConfig.has_key(profile):
            cls._defaultConfig[profile] = DefaultConfigWrapper(cfg, profile)
        
        res = cls._defaultConfig[profile]
        return res

class DefaultConfigWrapper(object):
    def __init__(self, config, profile):
        self.config = config
        self.profile = profile

    def __getattr__(self, name):
        attr = getattr(self.config, name)
        if name.startswith("get"):
            return lambda *args: attr(self.profile, *args)
        return attr
