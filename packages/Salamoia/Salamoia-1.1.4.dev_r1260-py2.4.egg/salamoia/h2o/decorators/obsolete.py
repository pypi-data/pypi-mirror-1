from salamoia.h2o.exception import *

def obsolete(func):
    name = func.func_name
    def obs(*args, **kwargs):
        raise ObsoleteException, '%s is obsolete' % (name)

    obs.func_name = name
    return obs


def willobsolete(func):
    name = func.func_name
    def obs(*args, **kwargs):
        from salamoia.h2o.logioni import Ione
        Ione.warning('%s will be obsoleted', name) 
        return func(*args, **kwargs)

    obs.func_name = name
    return obs



# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
