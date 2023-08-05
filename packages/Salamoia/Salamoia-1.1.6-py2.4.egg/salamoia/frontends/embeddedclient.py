from salamoia.h2o.logioni import * 
from salamoia.h2o.container import *
from salamoia.frontends.config import Config

import traceback

try:
    from salamoia.nacl.backend import Backend
except:
    print "GOT EXCEPTION IMPORTING BACKEND"
    raise

class FakeNaclOptions(object):
    def __init__(self):
        pass

class EmbeddedClient(object):
    def __init__(self, profile=None):
        self.profile = profile
	Ione.setLogMode('syslog')
        cfg = Config()

        Backend.options = FakeNaclOptions()
        Backend.options.profile = cfg.get(profile, 'naclprofile', profile)
        #setFakeContainer(True)
        
        self._backendInfo = {
            "naclUptime": 'fake',
            "suffix": cfg.get(profile, 'suffix', ''),
	    "loggedUsers":[''],
	    "hostname":'embedded'
            }

        try:
            self.control = Backend.defaultBackendClass()().controlClass()()
	except:
            traceback.print_exc()
            raise

    def connect(self):
        pass

    def backendInfo(self, action):        
        return self._backendInfo[action]

    def __getattr__(self, name):
        return EmbeddedClientWrapper(getattr(self.control, name))

class EmbeddedClientWrapper(object):
    def __init__(self, method):
        self.method = method

    def __call__(self, *args, **kwargs):
        res = self.method(*args, **kwargs)
        if isinstance(res, Object):
            #print "RESURRECTING", res
            res = res.resurrect()
            #print 'GOT', res
        return res
