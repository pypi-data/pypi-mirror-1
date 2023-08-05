from salamoia.utility.cache import ObjectCache
from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import FetchError

pyid = id

class BackendObjectCache(ObjectCache):
    def __init__(self):
        Ione.log("BackendObjectCache init")
        super(BackendObjectCache, self).__init__()
    
    def baseFetch(self, id):
        id = id.lower()
        if id in self.ocache:
            return self.ocache[id]
        try:
            obj = super(BackendObjectCache, self).baseFetch(id)
        except FetchError:
            self.ocache[id] = None
            raise
        self.ocache[id] = obj
        return obj

    def _cachedObject(self, id):
        return self.ocache.get(id)

    def store(self, obj, mode="auto"):
        res = super(BackendObjectCache, self).store(obj, mode)
        self.ocache[obj.id.lower()] = obj
        self.invalidateSearchCacheAffectedBy(obj) # TODO: be a bit more intelligent
        return res

    def search(self, spec):
        """
        Cached search
        """
        specKey = spec.__repr__()
        
        if specKey in self.searchCache:
            return self.searchCache[specKey]
        res = super(BackendObjectCache, self).search(spec)
        self.searchCache[specKey] = res
        return res

    def delete(self, obj):        
        res = super(BackendObjectCache, self).delete(obj)
        if obj.id in self.ocache:
            del self.ocache[obj.id]
        self.invalidateSearchCache() # TODO: be a bit more intelligent
        return res

    def cacheControl(self, action, *args):
        Ione.log("Invalidating cache on client request")
        # TODO: access control
        Ione.log("arg", action)
        self.invalidateCaches()
        if action == "invalidate":
            self.invalidateCaches()

        return 0

    def invalidateSearchCacheAffectedBy(self, obj):
        self.invalidateSearchCache()

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
