from salamoia.h2o.config     import Config
from salamoia.h2o.xmlserver  import Server
from salamoia.h2o.daemonizer import Daemonizer
from salamoia.h2o.logioni    import Ione
from salamoia.h2o.decorators import lazymethod, obsolete, abstract
from salamoia.h2o.servicedispatcher  import ServiceDispatcher

from optparse import OptionParser

__all__ = ['Backend']

class Backend(object):
    """
    The backend is the heart of the NACL server.
    Each backend provides a service to a centralized repository
    (LDAP, mysql etc) containing configuration dada, and interfaces
    the client to it.

    It also governs the triggering of actions (scripts) when
    some data changes
    """
    
    @classmethod
    @lazymethod
    def defaultBackend(cls):
        """
        Implements singleton pattern:
        every time this class method is invoked
        the very same object will be returned.
        
        The class of the object depends on the subclass of which the defaultBackend method
        is first invoked. The first thing an application needs to do is to obtain a defaultBackend
        from the class it wants to be the specific backend class, for example nacl startup script will
        load NACLBackend.defaultBackend().

        TODO: make it thread-local, so that the same application may run multiple backends.
              not trivial, because new request servicingthreads spawned from the backend thread need to inherit
              this value.
        """

        return cls()

    @classmethod
    @obsolete
    def defaultProfile(cls):
        pass

    def __init__(self):
        """
        Constructor
        """
        self.daemonizer = Daemonizer(self.name)

        self.serviceDispatcher = ServiceDispatcher()

    @classmethod
    def prepare(cls):
        """
        Called initially to prepare the backend machinery.

        Usually prepares the option parser and parses the initial options.

        May be overriden
        """
        cls.prepareOptions()
        cls.parseOptions()

    @classmethod
    def prepareOptions(cls):
        """
        Subclasses can add their own options to the parser.
        This method is called to prepare the parse with
        common options.

        Subclasses which override this method should
        calle the superclass's implementation first.
        """
        cls.optionParser = OptionParser()
        cls.optionParser.add_option('-c', '--config',
                                     action='store', type='string', dest='config',
                                     default=None,
                                     help="config file")
        cls.optionParser.add_option('-f', '--foreground',
                                     action='store_true', dest='foreground',
                                     default=True,
                                     help="don't put in background")
        cls.optionParser.add_option('-b', '--background',
                                     action='store_false', dest='foreground',
                                     help="force put in background")

    @classmethod
    def parseOptions(cls):
        """
        This method does the actual command line parameters parsing.
        
        The result of the parsing is stored in the 'options' and 'args'
        instance variables.
        """
        options, args = cls.optionParser.parse_args()
        cls.options = options
        cls.args = args

    @abstract
    def configFilenames(self):
        """
        Every concrete subclass of backend must override this method
        and return a list of filenames (left to right overriding).

        The filenames will be tilde expanded by the caller
        """

    def _makeServer(self):
        """
        Private method. 
        Constructs the self.server object
        """

        cfg = Config()
        port = cfg.getint('backend', "port", 12346)

        self.port = port
        
        self.server = Server(port, 0, self.serviceDispatcher)        

    def run(self):
        """
        Main entry point.
        Subclasses may override this but generally
        is better to override the controller.

        Configuration option preparing and parsing is started here
        """
        
        if not self.options.foreground:
            Ione.setLogMode('syslog')
            self.daemonizer.daemonize()
        else:
            Ione.setLogMode('stderr')

        if self.options.config:
            Config.setConfigFile(self.options.config)

        self._makeServer()

        # obsolete
        self.control = None

        Ione.log("%s server starting", self.name)
        self.server.serv()
        Ione.log("%s server exiting correctly", self.name)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
