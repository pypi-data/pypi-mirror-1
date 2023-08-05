from salamoia.h2o.logioni import Ione
from salamoia.h2o.schema import Schema, EntityDescription, SingletonDescription, IAdapterDescription

from salamoia.h2o.decorators import lazy
from salamoia.nacl.ldap.object import LDAPObject
from salamoia.h2o.protocols import (Interface, DelegatingAdapter, declareAdapter, adapt, NO_ADAPTER_NEEDED,
                                    declareMultiAdapter, multiAdapt)
from salamoia.h2o.generics import Multicall, Any
from salamoia.h2o.functional import partial, rpartial

class ILdapSchemaDefinition(Interface):
    pass

class ILdapAdapterDefinition(Interface):
    pass

class AdapterDefinitionAdapter(DelegatingAdapter):
    def registerAdapter(self, schema):
        self.parent = schema

        if len(self.for_) == 1:
            if self.factory:
                declareAdapter(self.factory, 
                               [self.parent.interface], forProtocols=[self.for_[0]])
            else:
                declareAdapter(lambda x: self.parent, 
                               [self.parent.interface], forProtocols=[self.for_[0]])
                declareAdapter(NO_ADAPTER_NEEDED, 
                               [self.parent.interface], forObjects=[self.parent])
        else:
            declareMultiAdapter(self.factory or self.constructFromAdaptation, 
                                [self.parent.interface], forProtocols=[self.for_])

declareAdapter(AdapterDefinitionAdapter, [ILdapAdapterDefinition], forProtocols=[IAdapterDescription])

class DefinitionAdapter(DelegatingAdapter):
    """
    This adapter adapts a schema definition description to a ldap specific schema definition.

    The difference is that a ldap specific definition knows about specific ldap classes like LDAPObject
    and is bound to a Schema (LDAPSchema) object.

    There can be multiple sepcific schema definition adapter for each schema definition
    """

    @lazy
    def containerClass(self):
        if self.container:
            return self.parent.classMap[self.container]

    def mergedInSchema(self, schema):
        #self.parent = schema
        self.schema = schema

        self.adapters = ILdapAdapterDefinition.conformingItems(self.children)
        Multicall(self.adapters).registerAdapter(self)
            

class EntityAdapter(DefinitionAdapter):
    @lazy
    def schemaClass(self):
        class SchemaClass(LDAPObject):
            def __init__(self):
                # fix this using closure local variable
                super(self.__class__, self).__init__()

                for attr in self.schema.attributes:
                    initial = attr.evalInitial(self)
                    setattr(self, attr.name, initial)

            objectClasses = self.subject.ldap.objectClasses.objectClasses
            primaryObjectClass = self.subject.ldap.objectClasses.structural                

            # TODO: obsolete this. access type map from schema directly
            attributeMap = {}
            for attr in self.subject.ldap.mappings:
                attributeMap[attr.ldap] = attr.name

            _attributeTypeMap = {}
            for attr in self.subject.attributes:
                if attr.type is not None:
                    _attributeTypeMap[attr.name] = attr.type

            keyAttribute = self.subject.keyAttribute

            schema = self

        SchemaClass.__name__ = str(self.subject.name)

        return SchemaClass

    @property
    def containerClass(self):
        return self.schema.classMap[self.container]

class SingletonAdapter(DefinitionAdapter):
    @lazy
    def schemaClass(self):
        class SchemaSingleton(LDAPObject):
            objectClasses = self.ldap.objectClasses.objectClasses
            primaryObjectClass = self.ldap.objectClasses.structural                

            attributeMap = {}
            _attributeTypeMap = {}

            keyAttribute = self.dn.split('=')[0]

            schema = self

        SchemaSingleton.__name__ = "%s-singleton" % (str(self.name))        

        return SchemaSingleton

    def absoluteDN(self):
        if not self.container:
            return self.dn

        parent = self.schema.classMap[self.container]
        parentDN = parent.schema.absoluteDN()
    
        assert parentDN

        return self.dn + ',' + parentDN


declareAdapter(EntityAdapter, [ILdapSchemaDefinition], forTypes=[EntityDescription])
declareAdapter(SingletonAdapter, [ILdapSchemaDefinition], forTypes=[SingletonDescription])

class LDAPSchema(Schema):
    """
    >>> s = LDAPSchema()
    >>> s.definitions
    {}
    """
    def __init__(self):
        super(LDAPSchema, self).__init__()

        self.classMap = {}
        self.reverseClassMap = {}

        self.objectClassMap = {}
        self.reverseObjectClassMap = {}
        
    def mergeDefinition(self, definition):
        definition = ILdapSchemaDefinition(definition)
        self.definitions[definition.name] = definition

        cls = definition.schemaClass

        self.classMap[cls.schema.name] = cls
        self.reverseClassMap[cls] = cls.schema.name

        self.objectClassMap[cls.schema.name] = cls.primaryObjectClass
        self.reverseObjectClassMap[cls.primaryObjectClass] = cls.schema.name

        definition.mergedInSchema(self)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
