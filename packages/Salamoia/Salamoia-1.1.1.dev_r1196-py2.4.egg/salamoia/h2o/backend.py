from salamoia.h2o.xmlserver  import *
from salamoia.h2o.servicedispatcher  import ServiceDispatcher
from salamoia.h2o.reflection import *
from salamoia.h2o.acl        import *
from salamoia.h2o.exception  import *
from salamoia.h2o.daemonizer import *
from salamoia.h2o.logioni    import *
from salamoia.h2o.object     import *
from salamoia.nacl.partialfetcher import *
from salamoia.h2o.decorators.lazy import *

from optparse import OptionParser

class Backend(object):
    """
    The backend is the heart of the NACL server.
    Each backend provides a service to a centralized repository
    (LDAP, mysql etc) containing configuration dada, and interfaces
    the client to it.

    It also governs the triggering of actions (scripts) when
    some data changes
    """
    _registeredBackends = {}

    @classmethod
    def registerBackend(cls, name, backend):
        cls._registeredBackends[name] = backend
    
    @classmethod
    @lazymethod
    def defaultBackend(cls):
        """
        Implements singleton pattern:
        every time this class method is invoked
        the very same object will be returned.

        The class of that object is defined in the
        'defaultBackendClass' method.

        On first invocation it also sets the ClassExtender's
        default group to the default class.
        """

        defaultClass = cls.defaultBackendClass()
        res = defaultClass()
        res.profile = cls.defaultProfile()

        return res

    _defaultProfile = "Default"

    @classmethod
    def defaultProfile(cls):
        cfg = cls.configClass()
        profile = cfg.get("General", "profile", cls._defaultProfile)
        if cls.options.profile:
	    profile = cls.options.profile

        return profile

    @classmethod
    def defaultBackendClass(cls, profile=None):
        """
        Read the profile from the command line or
        if not present read it from the [General]profile
        property in the configuration file.
        
        Return the class associated with the backend
        readed from the [<profile>]backend property

        Backends register themselves with Backend.registerBackend()
        """
        if not profile:
            profile = cls.defaultProfile()

        cfg = cls.configClass()
        backend = cfg.get(profile, "backend", "")
        if not backend:
            raise "No backend"
        
        return cls._registeredBackends[backend]

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
                                     default=False,
                                     help="don't put in background")
        cls.optionParser.add_option('-b', '--background',
                                     action='store_false', dest='foreground',
                                     help="force put in background")
        cls.optionParser.add_option('-p', '--profile',
                                     action='store', type='string', dest='profile',
                                     default='',
                                     help="profile")

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

        cfg = self.configClass()
        port = cfg.getint(self.defaultProfile(), "port",
                          cfg.getint("General", "port", 12346))
        self.port = port
        
        s = Server(port, 0, self.serviceDispatcher)

        # obsolete
        self.control = None

        Ione.log("%s server starting, profile %s" % (self.name, self.defaultProfile()))
        s.serv()
        Ione.log("%s server exiting correctly" % (self.name))
