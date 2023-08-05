from salamoia.nacl.feeds import *
from salamoia.nacl.info.control import *
from salamoia.nacl.info.emailControl import *
from salamoia.nacl.transaction import *
from salamoia.nacl.cache import *
from salamoia.nacl.lock import *
from salamoia.nacl.fetchpattern import *
from salamoia.h2o.logioni import *

class BackendMixin(TransactionControl, BackendObjectCache, FeedControl, LockControl, StorageCollector, 
                   TemplateControl, MailControl, FetchPatternControl):
    """
    Add classes that extends the BackendControl as superclasses
    of this class.

    Backend specific mixins must be added in the backend specific BackendControl
    subclass, not here. (see nacl.ldap.ldapbackend.CachedLDAPBackendControl for example
    """
    
    def __init__(self):
        Ione.log("BackendMixin init")
        super(BackendMixin, self).__init__()

