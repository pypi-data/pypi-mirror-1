import sys, os 

class Daemonizer(object):
    """
    The daemonizer object handles the daemonizing under UNIX.

    Just call damonize() and you will be a daemon!

    You will need to use syslog to comunicate with the rest
    of the world.
    """
    
    def __init__(self, appname=None):
        """
        The appname will be used for naming the pid file
        """
        self.appname = appname
        
    def daemonize(self):
        """
        This method does the real job of daemonizing the process.
        Upon return from this method we are running a new process.
        This process is detached from the controlling terminal and session and cd to /
        
        It writes the pid to /var/run/appname.pid
        """

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1)
            
        # decouple from parent environment
        # Redirect standard file descriptors
        # Redirect standard file descriptors.
        stdin = '/dev/null'
        stdout = '/dev/null'
        stderr = '/dev/null'
        si = file(stdin, 'r')
        so = file(stdout, 'a+')
        se = file(stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
        
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent, print eventual PID before
                if self.appname:
                    try:
                        f = open('/var/run/%s.pid' % self.appname, "w")
                        print >>f, pid
                    except IOError:
                        print "Daemon PID %d" % pid
		sys.exit(0)
        except OSError, e: 
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1) 

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
