from salamoia.h2o.decorators import lazymethod

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

    def registerSchemaDescription(self, schema):
        """
        """
        self.schemaByName[schema.name] = schema

    def schemaDescriptionNamed(self, name):
        return self.schemaByName[name]
        

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
