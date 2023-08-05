def lizer(func):


    def pythonic(*targs):
        args = []
        for a in targs:
            if not isinstance(a, list):
                a = [a]
            args.append(a)
        args[0] = args[0][0] # self should not be a list!
        res = func(*args)
        if isinstance(res, list):
            res = res[0]
        return res

    pythonic.lized = func
        
    return pythonic

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
