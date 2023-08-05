from salamoia.utility.cache import ObjectCache
from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import FetchError

class BackendObjectCache(ObjectCache):
    def __init__(self):
        Ione.log("BackendObjectCache init")
        super(BackendObjectCache, self).__init__()
    
    def baseFetch(self, id):
        if id in self.cache:
            return self.cache[id]
        try:
            obj = super(BackendObjectCache, self).baseFetch(id)
        except FetchError:
            self.cache[id] = None
            raise
        self.cache[id] = obj
        return obj

    def _cachedObject(self, id):
        return self.cache.get(id)

    def store(self, obj, mode="auto"):
        res = super(BackendObjectCache, self).store(obj, mode)
        self.cache[obj.id] = obj
        self.invalidateSearchCacheAffectedBy(obj) # TODO: be a bit more intelligent
        return res

    def search(self, spec):
        #Ione.log("CACHE search(%s)" % (spec))
        specKey = spec.__repr__()
        
        if specKey in self.searchCache:
            return self.searchCache[specKey]
        res = super(BackendObjectCache, self).search(spec)
        self.searchCache[specKey] = res
        return res

    def delete(self, obj):
        res = super(BackendObjectCache, self).delete(obj)
        if obj.id in self.cache:
            del self.cache[obj.id]
        self.invalidateSearchCache() # TODO: be a bit more intelligent
        return res

    def cacheControl(self, action):
        Ione.log("Invalidating cache on client request")
        # TODO: access control
        if action == "invalidate":
            self.invalidateCaches()

        return 0

    def invalidateSearchCacheAffectedBy(self, obj):
        self.invalidateSearchCache()

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
