#import xmlrpc
from salamoia.h2o.decorators.lazy import *
import ldap,ldapurl
import sys
from string import *
from syslog import *
import threading

import time, sys

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


    @classmethod
    @lazymethod
    def defaultIone(cls):
        return cls()
    
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

        # used to store thread local logging blocks
        self.threadLocal = threading.local()

    def _log(self, *messages, **keywords):
        level = keywords.get('level', self._logLevel)

        # bugged. doesn't honor escapes (%%s)
        percentCount = messages[0].count("%s")
        if percentCount:
            messages = (messages[0] % messages[1:percentCount+1],) +  messages[percentCount+1:]

        message = ' '.join([str(x) for x in messages])

        if len(threading.enumerate()) > 1:
            threadName = "(%s) " % (threading.currentThread().getName())
        else:
            threadName = ""
        
        formatted = "%s: %s%s" % (self.logTypes[level], threadName, message)
    
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

    @classmethod
    def log(cls, *args, **keywords):
        cls.defaultIone()._log(*args, **keywords)

    @classmethod
    def warning(cls, *args, **keywords):
        keywords.update({'level': LOG_WARNING})
        cls.defaultIone()._log(*args, **keywords)

    @classmethod
    def error(cls, *args, **keywords):
        keywords.update({'level': LOG_ERR})
        cls.defaultIone()._log(*args, **keywords)

    @classmethod
    def exception(cls, msg, *args, **keywords):
        keywords.update({'level': LOG_ERR})

        msg = "%s: %s, %s" % (msg, sys.exc_type, sys.exc_value)
        cls.defaultIone()._log(msg, *args, **keywords)

    def write(self, *args, **keywords):
        self._log(*args, **keywords)

    @classmethod
    def setLogMode(cls, str):
        cls.defaultIone()._logMode = str

    @classmethod
    def time(cls, *args, **keywords):
        cls.defaultIone()._time(*args, **keywords)
