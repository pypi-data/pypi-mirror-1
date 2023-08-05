from salamoia.h2o.logioni import Ione
from salamoia.h2o.xmlparser import Element
from salamoia.h2o.bundle import Description

from salamoia.h2o import types

from salamoia.h2o.schemamanager import SchemaManager
from salamoia.h2o import dottedname
from salamoia.h2o.decorators import obsolete, abstract, partialProperty, lazy

from protocols import (protocolForURI, advise, declareImplementation, declareAdapter,
                       Interface, Attribute, declareMultiAdapter)
from salamoia.h2o.generics import Any, Each
from salamoia.h2o.functional import AttributeAccessor

from salamoia.h2o.xmltal import Engine, StringEngine, PythonEngine

class AbstractHookDescription(Element):
    """
    This is the base class for 'hook' descriptions (<hook> in attribute and <modificationHook> <creationHook> in entity)
    """

    attributes = ['handler', 'args']

    def activate(self):
        self.handler = dottedname.resolve(self.handler)

    @abstract
    def patchClass(self, cls):
        """
        This method will take a given class register with it the appropriate hooks
        """

    @lazy
    def hook(self):
        return self.handler(self.args)

class AttributeHookDescription(AbstractHookDescription):
    def patchClass(self, cls):
        lst = cls.hookMap.setdefault(self.parent.name, [])
        lst.append(self.hook)

class EntityHookDescription(AbstractHookDescription):
    def patchClass(self, cls):
        self.accessor(cls).append(self.hook)

class CreationHookDescription(EntityHookDescription):
    accessor = AttributeAccessor.creationHooks

class ModificationHookDescription(EntityHookDescription):
    accessor = AttributeAccessor.modificationHooks

class AttributeDescription(Element):
    attributes = ['name', 'default', 'initial', 'check', 'fixed', 'syntax', 'type', 'required']

    childClasses = {'hook': AttributeHookDescription}

    def init(self):
        super(AttributeDescription, self).init()

        # python-ldap doesn't tolerate unicode
        self.name = str(self.name)

        self.required = self.required != "yes"

        self.hooks = [x for x in self.children if isinstance(x, AttributeHookDescription)]

        if self.type == '':
            self.type = None

        # handle List(itemType=..)
        self._itemType = None
        if self.type is not None:
            splitType = self.type.split(':')
            if len(splitType) == 2:
                self.type = splitType[0]
                self.itemType = splitType[1]

            self.type = getattr(types, self.type)
            if self._itemType:
                self.type = self.type(itemType=self._itemType)
            else:
                self.type = self.type()

    def __repr__(self):
        return "<Attr %s, %s>" % (self.name, self.default)

    def evalDefault(self, context):
        return self.eval(StringEngine, context, self.default)

    def evalInitial(self, context):
        if self.type and self.initial == '':
            return self.type.defaultValue()
        return self.eval(StringEngine, context, self.initial)

    def evalCheck(self, context):
        return self.eval(PythonEngine, context, self.check)

    def activate(self):
        """
        this is needed because hooks needs activation for resolving dotted name.

        TODO: avoid having dummy methods like this
        """
        for c in self.children:
            if hasattr(c, 'activate'):
                c.activate()

class ObjectClass(Element):
    attributes = ['name']

    def __repr__(self):
        return "<ObjectClass %s>" % (self.name)

class ObjectClasses(Element):
    childClasses = {'objectClass': ObjectClass}

    attributes = ['structural']

    def init(self):
        super(ObjectClasses, self).init()
        
        # python-ldap doesn't tolerate unicode
        self.objectClasses = [str(x.name) for x in self.children]
        
        if len(self.objectClasses) == 0:
            self.objectClasses.append(self.structural)

    def __repr__(self):
        return "<ObjectClasses %s>" % (self.structural)

class Mapping(Element):
    attributes = ['name', 'ldap']

    def init(self):
        super(Mapping, self).init()

        # python-ldap doesn't tolerate unicode
        self.name = str(self.name)
        self.ldap = str(self.ldap)

    def __repr__(self):
        return "<Mapping %s -> %s>" % (self.name, self.ldap)

class ILdapDescription(Interface):
    dn = Attribute('distinguished name')

class Ldap(Element):
    advise(instancesProvide=[ILdapDescription])

    childClasses = {'objectClasses': ObjectClasses, 'mapping': Mapping}

    attributes = ['dn']

    def init(self):
        super(Ldap, self).init()
        
        self.objectClasses = [x for x in self.children if isinstance(x, ObjectClasses)]
        if self.objectClasses:
            self.objectClasses = self.objectClasses[0]
        else:
            raise "Required", "objectClasses"

        self.mappings = [x for x in self.children if isinstance(x, Mapping)]        

    def __repr__(self):
        return "<Ldap %s>" % (self.dn)

class IAdapterDescription(Interface):
    for_ = Attribute('interaface the adapter adapts')
    factory = Attribute('adapter factory')

class AdapterDescription(Element):
    """
    Adapters defined this way are multiadapters on two arguments:
    schema and subject

    The schema is the schema objects of the adapted entity 
    """
    advise(instancesProvide=[IAdapterDescription])

    attributes = ['for', 'factory']

    def init(self):
        super(AdapterDescription, self).init()

        self.for_ = Each(self.__dict__['for'].split(',')).strip()

    def activate(self):
        def resolveFor(for_):
            if isinstance(for_, basestring):
                if for_.startswith('http://'):
                    return protocolForURI(for_)
                return dottedname.resolve(for_)
        self.for_ = tuple(map(resolveFor, self.for_))


        if self.factory:
            self.factory = dottedname.resolve(self.factory)
        else:
            self.factory = None
    
    declareImplementation(object, instancesProvide=[protocolForURI('http://interfaces.salamoia.org/IAttributeStorable')])

    def constructFromAdaptation(self, schema, subject):
        """
        Creates an object of the entity and sets the
        key attribute to the subjet of the adaptation.

        It is common that the subject for this forms of adaptation will
        be some primitive type (usually a basestring).

        TODO: Create an interface IAttributeStorable and adapt to it

        TODO: find a nicer way to do multi adaptation. this is ugly
        """
        #res = schema.definitions[self.parent.name].schemaClass()
        res = self.parent.schemaClass()

        value = protocolForURI('http://interfaces.salamoia.org/IAttributeStorable')(subject)

        setattr(res, res.schema.keyAttribute, value)
        res.resurrect()

        return res

class Definition(Element):
    childClasses = {'attribute': AttributeDescription, 'ldap': Ldap, 'adapter': AdapterDescription,
                    'creationHook': CreationHookDescription, 'modificationHook': ModificationHookDescription}

    attributes = ['name', 'container', 'keyAttribute', 'interface']

    def init(self):
        super(Definition, self).init()

        # the name attributes here is not nice but does not conflict with the class variable
        # because it is used only in __init__
        self.attributes = [x for x in self.children if isinstance(x, AttributeDescription)]

        self.hooks = [x for x in self.children if isinstance(x, EntityHookDescription)]

        self.ldap = self.findChild(Ldap)

        self.root().registerDefinition(self)

    def activate(self):
        if self.interface and isinstance(self.interface, basestring):
            if self.interface.startswith('http://'):
                self.interface = protocolForURI(self.interface)
            else:
                self.interface = dottedname.resolve(self.interface)

        for c in self.children:
            if hasattr(c, 'activate'):
                c.activate()

    def absoluteDN(self):
        return None

class SingletonDescription(Definition):
    def init(self):
        super(SingletonDescription, self).init()

        self.dn = self.ldap.dn

    def __repr__(self):
        return "<SingletonDescription %s>" % (self.name)

class EntityDescription(Definition):
    def __repr__(self):
        return "<EntityDescription %s>" % (self.name)

class SchemaDescription(Description):
    childClasses = {'object': SingletonDescription, 'entity': EntityDescription}
    
    attributes = ['name', 'version']

    dtd = "schema.dtd"
    rootElementName="schema"

    # speedup delevopment
    validable = False

    def __repr__(self):
        return "<SchemaDescription %s>" % (self.name)

    def __init__(self, filewrapper, validate=True):
        self.registeredDefinitions = []

        super(SchemaDescription, self).__init__(filewrapper, validate)

    def registerDefinition(self, definition):
        if definition.name in [x.name for x in self.registeredDefinitions]:
            Ione.warning("double registration of definition", definition.name)
        assert not definition.name in [x.name for x in self.registeredDefinitions]

        self.registeredDefinitions.append(definition)

    def activate(self):
        """
        Called when the Bundle is activated.

        Register the schema description to the SchemaManager
        """        
        SchemaManager.defaultManager().registerSchemaDescription(self)

        for c in self.children:
            if hasattr(c, 'activate'):
                c.activate()

class ISchema(Interface):
    advise(equivalentProtocols=[protocolForURI("http://interfaces.salamoia.org/ISchema")])

class Schema(object):
    advise(instancesProvide=[ISchema])

    def __init__(self):
        """
        Create an empty schema
        """
        self.definitions = {}

    def merge(self, description):
        """
        Merge a schema description in this schema
        """
        for definition in description.registeredDefinitions:
            self.mergeDefinition(definition)

    @abstract
    def mergeDefinition(self, definition):
        pass

    @classmethod
    def mergeFrom(cls, descs):
        """
        Return a merged schema from a list of schema descriptions
        """
        schema = cls()
        for d in descs:
            schema.merge(d)
        return schema

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
