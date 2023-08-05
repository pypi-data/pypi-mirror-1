from copy import deepcopy

# from ASPN
# This recipe provides a decorator for keeping mutable default function values fresh between calls.
def freshdefaults(f):
    "wrap f and keep its default values fresh between calls"
    fdefaults = f.func_defaults
    def refresher(*args, **kwds):
        f.func_defaults = deepcopy(fdefaults)
        return f(*args, **kwds)
    return refresher
