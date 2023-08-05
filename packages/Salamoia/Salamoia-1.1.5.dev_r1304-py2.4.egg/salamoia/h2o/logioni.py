#import xmlrpc
from salamoia.h2o.decorators import lazymethod
from salamoia.h2o.functional import partial

import sys
#from string import *
from syslog import syslog, openlog, LOG_PID, LOG_INFO, LOG_WARNING, LOG_ERR, LOG_CRIT, LOG_ALERT, LOG_EMERG
import threading

import time, traceback

MODE=("syslog", "stderr")
LEVEL=(LOG_INFO, LOG_WARNING, LOG_ERR, LOG_CRIT, LOG_ALERT, LOG_EMERG)

__all__ = ['Ione', 'LOG_INFO', 'LOG_WARNING', 'LOG_ERR', 'LOG_CRIT', 'LOG_ALERT', 'LOG_EMERG']

YELLOW = "\033[01;33m"
GREEN = "\033[01;32m"
BLUE = "\033[01;34m"
RED = "\033[01;31m"
RESET = "\033[00m"

class Ione(object):
    """
    A flexible logger.

    TODO: implement some kind of per object logging, exploiting
    that many objects inherit from Ione...
    """
    
    LOGlevel=LEVEL[0]
    logTypes = {LOG_INFO: 'Info', LOG_ERR: 'Error', LOG_WARNING: 'Warning',
                LOG_CRIT: 'Critical', LOG_ALERT: 'Alert', LOG_EMERG: 'Emergency'}

    highlightedMessageID = ''

    @classmethod
    @lazymethod
    def defaultIone(cls):
        return cls()
    
    def __init__(self, mode=None, level=LEVEL[0]):
        super(Ione, self).__init__()

        if not mode:
            mode = MODE[1]
        self._logMode = mode
        self._logLevel = level
        # setting syslog defaults that makes sense
        openlog('nacl', LOG_PID)

        self.last_timestamp = time.time()
        self.last_message = ""

        # used to store thread local logging blocks
        self.threadLocal = threading.local()

    def _log(self, *messages, **keywords):
        level = keywords.get('level', self._logLevel)

        percentCount = messages[0].count("%s") - messages[0].count("%%s")
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
            color = RESET
            if level == LOG_ERR:
                color = RED
            if level == LOG_WARNING:
                color = YELLOW
            if keywords.get('msgid') == self.highlightedMessageID:
                color = GREEN
            print >>sys.stderr, "%s%s%s" % (color, formatted, RESET)

    def _time(self, *messages, **keywords):
        keywords.update({}) # lint warning

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

    warning = partial(log, level=LOG_WARNING)
    error = partial(log, level=LOG_ERR)

    @classmethod
    def traceback(cls, msg, *args, **keywords):
        tb = ''.join(traceback.format_stack()).replace('%s', '%%s')
        cls.warning(msg, *(args+(tb,)), **keywords)

    @classmethod
    def exception(cls, msg, *args, **keywords):
        keywords.update({'level': LOG_ERR})

        if keywords.get('traceback'):
            trace = ''.join(traceback.format_tb(sys.exc_info()[2])).replace('%s', '%%s')
            cls.error(trace, *args, **keywords)
            cls.error("-----")

        msg = "%s: %s, %s" % (msg, sys.exc_type, sys.exc_value)
        cls.error(msg, *args, **keywords)
        cls.error("----->")

    def write(self, *args, **keywords):
        self._log(*args, **keywords)

    @classmethod
    def setLogMode(cls, str):
        cls.defaultIone()._logMode = str

    @classmethod
    def time(cls, *args, **keywords):
        cls.defaultIone()._time(*args, **keywords)

    @classmethod
    def highlightMessagesWithID(cls, msgid):
        cls.highlightedMessageID = msgid

    @classmethod
    def logMethod(cls, func):
        def wrapper(*args, **kwargs):
            res = "ExCePtIoN"
            try:
                res = func(*args, **kwargs)
                return res
            finally:
                cls.log("Called", func, "args", args, kwargs, "returns", res)
        return wrapper

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
