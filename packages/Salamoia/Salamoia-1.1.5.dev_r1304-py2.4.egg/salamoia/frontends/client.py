import os
import traceback
from config import Config

from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import *
from salamoia.h2o.decorators import *

class Client(object):

    _defaultClient = {}
    _defaultEmbedded = False

    @classmethod
    @lazymethod
    def defaultClient(cls):        
        cfg = Config.defaultConfig()
        embedded = cfg.getboolean('general', 'embedded', cls._defaultEmbedded)
        clientClass = cls
        if embedded:
            from embeddedclient import EmbeddedClient
            clientClass = EmbeddedClient
        return clientClass()

    @classmethod
    def setDefaultEmbedded(cls, embedde):
        cls._defaultEmbedded = embedded

    def __init__(self, user="", password=""):
        self._client = None
        cfg = Config.defaultConfig()

        self._hostname = cfg.get('general', 'hostname', 'localhost')
        self._port = cfg.getint('general', 'port', 12346)
        self._sshHost = cfg.get('general', 'sshHost', None)
        self._localport = cfg.getint('general', 'localport', 12346)
        self._sshUser = cfg.get('general', 'sshuser', os.getenv('USER'))

        # TODO: NOT ALL CONFIGS SHOULD BE READ HERE, BUT ONLY Client RELATED
        # common options (like installDir) should go in class Frontend of in Config itself instead of here.
        # requiring import of client at early startup of oliva slows startup time
        #

        self._username = user
        self._password = password
            
    def connect(self):
        cfg = Config.defaultConfig()
        
        try:
            hostname = self._hostname
            port = int(self._port)
            localport = int(self._localport)
            
            username = self._username
            password = self._password

            if not username:
                username = cfg.get('general', 'username', os.getenv('USER'))
            if not password:
                password = cfg.get('general', 'password', '')

            if self._sshHost:
                from salamoia.h2o.sshtunnel import SSHTunnel
                self.tunnel = SSHTunnel(self._sshHost, localport, port, hostname)
                self.tunnel.run()
                self.tunnel.waitShell()
                hostname = 'localhost'
                port = localport

            import salamoia.h2o.xmlclient

            self._client =  salamoia.h2o.xmlclient.Client(hostname, port,
                                                          -1,
                                                          username, password,
                                                          interfacePair=self._interfacePair)
        except:
            Ione.setLogMode('stderr')
            Ione.exception('connecting')
            raise ConnectionError, "error connectinggx %s %s %s" % (hostname, port, username)

    @lazy
    def _interfacePair(self):
        """
        Override subclasses to provide customize pair of interfaces on which adapt arguments and return values
        before passing through.

        You can override this value on a per instance basis, simply setting a '_interfacePair' attribute
        """
        return None

    def __getattr__(self, name):
	try:
	    if self._client:
		if hasattr(self._client, name):
		    return getattr(self._client, name)
                    #return DebugClientWrapper(getattr(self._client, name))
		raise AttributeError, "NOT ATTR NAMED %s" % name
	    else:
		raise "CONNECTION EMPTY %s %s %s" % (self._client, self, self.__dict__)
        except AttributeError:
            raise
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

