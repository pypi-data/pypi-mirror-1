from salamoia.h2o.exception import *
from salamoia.h2o.logioni import Ione

def obsolete(func):
    name = func.func_name
    def obs(*args, **kwargs):
        raise ObsoleteException, '%s is obsolete' % (name)

    obs.func_name = name
    return obs


def willobsolete(func):
    name = func.func_name
    def obs(*args, **kwargs):
        Ione.warning('%s will be obsoleted', name) 
        return func(*args, **kwargs)

    obs.func_name = name
    return obs


