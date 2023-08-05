from salamoia.nacl.cache import *
from salamoia.nacl.search import *

class FLATBackendObjectCache(BackendObjectCache):
    def invalidateSearchCacheAffectedBy(self, obj):
        retainedCacheEntries = {}
        
        Ione.log("search cache", self.searchCache)
        for i in self.searchCache.keys():
            #print "CACHE ENTRY", i
            match = re.match("^' *max\(([^\)]*)\) *'$", i)
            if match:
                #print "MAX CACHE ENTRY", i, type(i)
                retainedCacheEntries[i] = self.searchCache[i]

                attr = match.group(1)
                cached = self.fetch(self.searchCache[i], [attr]).value[0]
                if int(getattr(obj, attr)) > int(getattr(cached, attr)):
                    retainedCacheEntries[i] = [obj.id]
                    #print "IS CACHED", [obj.id]

        super(FLATBackendObjectCache, self).invalidateSearchCacheAffectedBy(obj)
                
        self.searchCache.update(retainedCacheEntries)
       # print "LEFT IN SEARCH CACHE", retainedCacheEntries
