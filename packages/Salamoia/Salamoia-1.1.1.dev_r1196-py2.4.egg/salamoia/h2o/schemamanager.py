from salamoia.h2o.decorators.lazy import *

__all__ = ['SchemaManager']

class SchemaManager(object):
    """
    The schema manager keeps track of registered schemas
    """

    @classmethod
    @lazymethod
    def defaultManager(cls):
        """
        Returns the global bundle manager
        """
        return SchemaManager()

    def __init__(self):
        self.schemaByName = {}

    def registerSchema(self, schema):
        """
        """
        self.schemaByName[schema.name] = schema

    def schemaNamed(self, name):
        return self.schemaByName[name]
        
