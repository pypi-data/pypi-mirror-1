import os
import traceback
from config import Config

from salamoia.h2o.exception import *

class Client(object):

    _defaultClient = {}
    _defaultProfile = None
    _defaultEmbedded = False

    @classmethod
    def defaultClient(cls, profile=None):
        if not cls._defaultProfile:
            cfg = Config()
            cls._defaultProfile = cfg.get('Connection', 'profile', 'DefaultProfile')
            
        if not profile:
            profile = cls._defaultProfile

        if not cls._defaultClient.has_key(profile):
            embedded = cfg.getboolean(profile, 'embedded', cls._defaultEmbedded)
            clientClass = cls
            if embedded:
                from embeddedclient import EmbeddedClient
                clientClass = EmbeddedClient
            cls._defaultClient[profile] = clientClass(profile)
        
        res = cls._defaultClient[profile]
        return res

    @classmethod
    def setDefaultProfile(cls, profile):
        cls._defaultProfile = profile

    @classmethod
    def setDefaultEmbedded(cls, embedde):
        cls._defaultEmbedded = embedded


    def __init__(self, profile, user="", password=""):
        self._client = None
        cfg = Config()
        self._profile = profile

        self._hostname = cfg.get(self._profile, 'hostname', 'localhost')
        self._port = cfg.getint(self._profile, 'port', 12346)
        self._sshHost = cfg.get(self._profile, 'sshHost', None)
        self._localport = cfg.getint(self._profile, 'localport', 12346)
        self._sshUser = cfg.get(self._profile, 'sshuser', os.getenv('USER'))

        # TODO: NOT ALL CONFIGS SHOULD BE READ HERE, BUT ONLY Client RELATED
        # common options (like installDir) should go in class Frontend of in Config itself instead of here.
        # requiring import of client at early startup of oliva slows startup time
        #
        # TODO: refactor cfg.get using defaultProfile 
        #self._installDir = cfg.getpath(self._profile, 'installdir', "/tmp")
	#self._templatesDir = cfg.getpath(self._profile, 'templatesdir', self._installDir / "templates")
        #self._macroDir = cfg.getpath(self._profile, 'macrodir', self._installDir / "macros")
	
        if user:
            self._username = user
        else:
            self._username = cfg.get(self._profile, 'username', os.getenv('USER'))
        if password:
            self._password = password
        else:
            self._password = cfg.get(self._profile, 'password', '')
            
    def connect(self):

        try:
            hostname = self._hostname
            port = int(self._port)
            localport = int(self._localport)
            username = self._username
            password = self._password

            if self._sshHost:
                from salamoia.h2o.sshtunnel import SSHTunnel
                self.tunnel = SSHTunnel(self._sshHost, localport, port, hostname)
                self.tunnel.run()
                self.tunnel.waitShell()
                hostname = 'localhost'
                port = localport

            import salamoia.h2o.xmlclient

            self._client =  salamoia.h2o.xmlclient.Client(hostname,
                                            port,
                                            -1,
                                            username,
                                            password)            
        except:
            raise ConnectionError, "error connectinggx"

    def __getattr__(self, name):
	try:
	    if self._client:
		if hasattr(self._client, name):
		    return getattr(self._client, name)
                    #return DebugClientWrapper(getattr(self._client, name))
		raise "NOT ATTR NAMED %s" % name
	    else:
		raise "CONNECTION EMPTY %s %s %s" % (self._client, self, self.__dict__)
	except:
	    pass
	
    def leave(self):
	try:
	    self._client.leave()
	except:
            raise ConnectionError, "error disconnecting"	

class DebugClientWrapper(object):
    """
    you can hook this class in the __getattr__ method of Client in order
    to sniff the returned values
    """
    def __init__(self, method):
        self.method = method

    def __call__(self, *args, **kwargs):
        res = self.method(*args, **kwargs)
        print "RETURING from client", res
        return res

