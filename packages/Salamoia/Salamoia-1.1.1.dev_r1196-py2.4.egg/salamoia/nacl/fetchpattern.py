from salamoia.h2o.logioni import Ione
from salamoia.h2o.exception import *

class FetchPatternControl(object):
    """
    this class extends the api offering compact form of frequent called
    base api methods (search & fetch), avoiding unneeded exchange of RPC calls
    """

    def fetchPattern(self, searchSpec, attributes=None):
        """
        a shorthand combination of search and fetch.
        using it is faster because less requests travel the rpc
        """
        Ione.log("fetch pattern pattern: %s attributes: %s", searchSpec, attributes)
        return self.fetch(self.search(searchSpec), attributes)

    def fetchOnePattern(self, searchSpec, attributes=None):
        """
        a shorthand combination of search and fetch.
        using it is faster because less requests travel the rpc
        """
        #Ione.log("fetch one pattern", searchSpec)
        return self.fetch(self.searchOne(searchSpec), attributes)

    def searchOne(self, searchSpec):
        """
        ensures that only one result is searched, otherwise raises and error.
        it's useful in order to avoid a useless transfer of a ObjectContainer object
        wrapping a list of length one...
        """
        res = self.search(searchSpec)
        if len(res) != 1:
            raise SearchError , "One and only one should match"
        return res[0]
