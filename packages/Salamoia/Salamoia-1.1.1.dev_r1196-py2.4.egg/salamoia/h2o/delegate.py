from salamoia.h2o.logioni import Ione

class DelegatedObject(object):
    def __getattr__(self, name):
        Ione.log("DELEGATED", self.delegate, "getattrs", name)
        if name in [x for x in dir(self.delegate) if x[0] != '_']:
            return getattr(self.delegate, name)
        else:
            return super(DelegatedObject, self).__getattr__(name)
