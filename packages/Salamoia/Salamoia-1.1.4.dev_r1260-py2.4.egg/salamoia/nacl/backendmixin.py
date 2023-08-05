from salamoia.nacl.feeds import FeedControl
from salamoia.nacl.transaction import TransactionControl
from salamoia.nacl.cache import BackendObjectCache
from salamoia.nacl.lock import LockControl
from salamoia.nacl.fetchpattern import FetchPatternControl
from salamoia.h2o.logioni import Ione

class BackendMixin(TransactionControl, BackendObjectCache, FeedControl, LockControl, FetchPatternControl):
    """
    Add classes that extends the BackendControl as superclasses
    of this class.

    Backend specific mixins must be added in the backend specific BackendControl
    subclass, not here. (see nacl.ldap.ldapbackend.CachedLDAPBackendControl for example
    """
    
    def __init__(self):
        Ione.log("BackendMixin init")
        super(BackendMixin, self).__init__()


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
