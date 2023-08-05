#import xmlrpc
import ldap,ldapurl
import sys
from string import *
from syslog import *

import time

MODE=("syslog", "stderr")
LEVEL=(LOG_INFO, LOG_WARNING, LOG_ERR, LOG_CRIT, LOG_ALERT, LOG_EMERG)

class Ione(object):
    """
    A flexible logger.

    TODO: implement some kind of per object logging, exploiting
    that many objects inherit from Ione...
    """
    
    LOGlevel=LEVEL[0]
    logTypes = {LOG_INFO: 'Info', LOG_ERR: 'Error', LOG_WARNING: 'Warning',
                LOG_CRIT: 'Critical', LOG_ALERT: 'Alert', LOG_EMERG: 'Emergency'}

    _default = None
    def defaultIone(cls):
        if not cls._default:
            cls._default = cls()
        return cls._default

    defaultIone = classmethod(defaultIone)
    
    def __init__(self, mode=None, level=LEVEL[0]):
        super(Ione, self).__init__()

        if not mode:
            mode = MODE[0]
        self._logMode = mode
        self._logLevel = LEVEL[0]
        # setting syslog defaults that makes sense
        openlog('nacl', LOG_PID)

        self.last_timestamp = time.time()
        self.last_message = ""

    def _log(self, *messages, **keywords):
        level = keywords.get('level', self._logLevel)

        message = ' '.join([str(x) for x in messages])
        formatted = "%s: %s" % (self.logTypes[level], message)
    
        if self._logMode == MODE[0]:
            syslog(level, formatted)
        elif self._logMode == MODE[1]:
            print >>sys.stderr, formatted

    def _time(self, *messages, **keywords):
        message = ' '.join([str(x) for x in messages])
        delta = time.time() - self.last_timestamp
        #print >>sys.stderr, self.last_message, "took", round(delta, 4), "s"
        print >>sys.stderr, "took", round(delta, 4), "s"
        self.last_timestamp = time.time()
        self.last_message = message

        print >>sys.stderr, "now:", message, " ... ",
        sys.stderr.flush()
        
    def log(cls, *args, **keywords):
        cls.defaultIone()._log(*args, **keywords)

    log = classmethod(log)

    def write(self, *args, **keywords):
        self._log(*args, **keywords)

    def setLogMode(cls, str):
        cls.defaultIone()._logMode = str

    setLogMode = classmethod(setLogMode)

    def time(cls, *args, **keywords):
        cls.defaultIone()._time(*args, **keywords)
        #pass

    time = classmethod(time)

