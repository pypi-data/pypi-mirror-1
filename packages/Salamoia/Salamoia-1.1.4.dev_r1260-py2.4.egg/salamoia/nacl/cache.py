from salamoia.h2o.cache import ObjectCache
from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import FetchError

class BackendObjectCache(ObjectCache):
    def __init__(self):
        Ione.log("BackendObjectCache init")
        super(BackendObjectCache, self).__init__()
    
    def baseFetch(self, id):
        if id in self.cache:
            #Ione.log("HIT CACHE baseFetch(%s)" % (id))
            return self.cache[id]
        #Ione.log("MISS CACHE baseFetch(%s)" % (id))
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
        #Ione.log("CACHE store(%s)" % (obj.id))
        res = super(BackendObjectCache, self).store(obj, mode)
        self.cache[obj.id] = obj
        self.invalidateSearchCacheAffectedBy(obj) # TODO: be a bit more intelligent
        #self.invalidateSearchCache() # TODO: be a bit more intelligent
        return res

    def search(self, spec):
        #Ione.log("CACHE search(%s)" % (spec))
        specKey = spec.__repr__()
        
        if specKey in self.searchCache:
            #Ione.log("HIT CACHE search(%s)" % (spec))
            return self.searchCache[specKey]
        #Ione.log("MISS CACHE search(%s)" % (spec))
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
