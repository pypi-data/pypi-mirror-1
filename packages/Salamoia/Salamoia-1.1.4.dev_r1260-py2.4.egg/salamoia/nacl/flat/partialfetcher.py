from salamoia.nacl.partialfetcher import *

class FLATPartialFetcher(PartialFetcher):
    def __call__(self, id):
        # pseudo hack. non reentrant. 
        #Since mixins can hook before baseFetch we cannot modify the method signature

        self.controller._fetchAttributes = self.attributes
        obj = self.controller.baseFetch(id)
        self.controller._fetchAttributes = None

        partial = self.controller.defaultPartialObject()(obj, self.attributes)
        return partial

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
