from pkg_resources import Environment, working_set

from salamoia.h2o.decorators import lazymethod
from salamoia.h2o.logioni import Ione

from salamoia.h2o.bundle import Bundle

__all__ = ['BundleManager']

class BundleManager(object):
    """
    The bundle manager keeps track of installed and active bundles
    """

    @classmethod
    @lazymethod
    def defaultManager(cls):
        """
        Returns the global bundle manager
        """
        return BundleManager()

    def __init__(self):
        self.bundles = {}

        # TODO: parametrize the bundlepath
        self.searchPath = ['/tmp/salamoia/bundles', 'bundles']

    def registerEgg(self, name, egg):
        """
        register a setuptools egg file, creating a Bundle for it
        """
        self.registerBundle(name, Bundle(egg))

    def registerBundle(self, name, bundle):
        """
        register a bundle.
        
        The bundle will be activated.
        """
        self.bundles[name] = bundle
        bundle.activate()        

    def refresh(self):
        """
        Searches the bundle path for new bundles and register them
        """
        env = Environment(self.searchPath)

        dists, errors = working_set.find_plugins(env)

        for egg in dists:
            if not self.bundles.has_key(egg.key):
                try:
                    self.registerEgg(egg.key, egg)
                except:
                    Ione.exception('Error loading bundle %s', egg, traceback=True)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
