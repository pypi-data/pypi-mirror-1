from salamoia.h2o.object import *

class PartialFetcher(object):
    def __init__(self, controller, attributes):
        self.controller = controller
        self.attributes = attributes

    def __call__(self, id):
        obj = self.controller.baseFetch(id)
        partial = self.controller.defaultPartialObject()(obj, self.attributes)
        return partial
