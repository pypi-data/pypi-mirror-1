from salamoia.h2o.logioni import *

class BackendMixin:
    """
    Add classes that extends the BackendControl as superclasses
    of this class.

    Backend specific mixins must be added in the backend specific BackendControl
    subclass, not here. 
    """
    
    def __init__(self):
        Ione.log("BackendMixin init")
#        super(BackendMixin, self).__init__()

