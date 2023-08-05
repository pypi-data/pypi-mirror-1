from salamoia.h2o.xmlparser import Element
from salamoia.h2o.bundle import Description

from salamoia.tales.tales import Context, ExpressionEngine
from salamoia.tales.expressions import StringExpr, PathExpr, NotExpr, DeferExpr
from salamoia.tales.pythonexpr import PythonExpr

from salamoia.h2o import types

from salamoia.h2o.schemamanager import SchemaManager

#from salamoia.nacl.interface import implements
#from salamoia.nacl import interface

# TAL CLASSES

class IntExpr(object):
    def __init__(self, name, expr, engine):
        self._s = expr = expr.lstrip()
        #self._c = engine.compile(expr)
                    
    def __call__(self, econtext):
        return int(self._s)
                        
    def __repr__(self):
        return '<IntExpr %s>' % `self._s`

def Engine():
    e = ExpressionEngine()
    reg = e.registerType
    for pt in PathExpr._default_type_names:
        reg(pt, PathExpr)
    reg('string', StringExpr)
    reg('python', PythonExpr)
    reg('not', NotExpr)
    reg('defer', DeferExpr)
    reg('int', IntExpr)
    #e.registerBaseName('modules', SimpleModuleImporter())
    return e

def StringEngine():
    e = Engine()
    del e.types['standard']
    e.registerType('standard', StringExpr)
    return e

def PythonEngine():
    e = Engine()
    del e.types['standard']
    e.registerType('standard', PythonExpr)
    return e

StringEngine = StringEngine()
PythonEngine = PythonEngine()

# XML PARSER CLASSESS

class Attribute(Element):
    attributes = ['name', 'default', 'initial', 'check', 'fixed', 'syntax', 'type']

    def init(self):
        super(Attribute, self).init()

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

    def eval(self, engine, context, expression):
        ctx = context.__dict__.copy()
        ctx['context'] = context
        return engine.compile(expression)(Context(engine, ctx))

    def evalDefault(self, context):
        return self.eval(StringEngine, context, self.default)

    def evalInitial(self, context):
        if self.type and self.initial == '':
            return self.type.defaultValue()
        return self.eval(StringEngine, context, self.initial)

    def evalCheck(self, context):
        return self.eval(PythonEngine, context, self.check)

class ObjectClass(Element):
    attributes = ['name']

    def __repr__(self):
        return "<ObjectClass %s>" % (self.name)

class ObjectClasses(Element):
    childClasses = {'objectClass': ObjectClass}

    attributes = ['structural']

    def init(self):
        super(ObjectClasses, self).init()
        
        self.objectClasses = [x.name for x in self.children]
        
        class FakeObjectClassElement(object):
            @staticmethod
            def getAttribute(name):
                return self.structural

        if len(self.objectClasses) == 1:
            self.objectClasses.append(ObjectClass(FakeObjectClassElement))

    def __repr__(self):
        return "<ObjectClasses %s>" % (self.structural)

class Mapping(Element):
    attributes = ['name', 'ldap']

    def __repr__(self):
        return "<Mapping %s -> %s>" % (self.name, self.ldap)

class Ldap(Element):
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

class Definition(Element):
    childClasses = {'attribute': Attribute, 'ldap': Ldap}

    attributes = ['name', 'container', 'keyAttribute']

    def init(self):
        super(Definition, self).init()

        # the name attributes here is not nice but does not conflict with the class variable
        # because it is used only in __init__
        self.attributes = [x for x in self.children if isinstance(x, Attribute)]

        self.ldap = self.findChild(Ldap)

        self.containerClass = None
        if self.container:            
            self.containerClass = self.root().classMap[self.container]

    def absoluteDN(self):
        return None

class Singleton(Definition):
    def init(self):
        from salamoia.nacl.ldap.object import LDAPObject

        super(Singleton, self).init()

        self.dn = self.ldap.dn

        class SchemaSingleton(LDAPObject):
            objectClasses = self.ldap.objectClasses.objectClasses
            primaryObjectClass = self.ldap.objectClasses.structural                

            attributeMap = {}
            _attributeTypeMap = {}

            keyAttribute = self.dn.split('=')[0]

            schema = self

        SchemaSingleton.__name__ = "%s-singleton" % (str(self.name))

        self.root().registerClass(SchemaSingleton)

    def absoluteDN(self):
        if not self.container:
            return self.dn

        parent = self.root().classMap[self.container]
        parentDN = parent.schema.absoluteDN()
    
        assert parentDN

        return self.dn + ',' + parentDN

class Entity(Definition):
    def init(self):
        from salamoia.nacl.ldap.object import LDAPObject

        super(Entity, self).init()

        class SchemaClass(LDAPObject):
            def __init__(self):
                super(self.__class__, self).__init__()

                for attr in self.schema.attributes:
                    initial = attr.evalInitial(self)
                    setattr(self, attr.name, initial)

            objectClasses = self.ldap.objectClasses.objectClasses
            primaryObjectClass = self.ldap.objectClasses.structural                

            # TODO: obsolete this. access type map from schema directly
            attributeMap = {}
            for attr in self.ldap.mappings:
                attributeMap[attr.ldap] = attr.name

            _attributeTypeMap = {}
            for attr in self.attributes:
                if attr.type is not None:
                    _attributeTypeMap[attr.name] = attr.type

            keyAttribute = self.keyAttribute

            schema = self

        SchemaClass.__name__ = str(self.name)

        self.root().registerClass(SchemaClass)


class SchemaDescription(Description):
    childClasses = {'object': Singleton, 'entity': Entity}
    
    attributes = ['name', 'version']

    dtd = "schema.dtd"
    rootElementName="schema"

    # speedup delevopment
    validable = False

    def __repr__(self):
        return "<SchemaDescription %s>" % (self.name)

    def __init__(self, filewrapper, validate=True):
        self.classMap = {}
        self.reverseClassMap = {}

        self.objectClassMap = {}
        self.reverseObjectClassMap = {}

        super(SchemaDescription, self).__init__(filewrapper, validate)

    def registerClass(self, cls):
        self.classMap[cls.schema.name] = cls
        self.reverseClassMap[cls] = cls.schema.name

        self.objectClassMap[cls.schema.name] = cls.primaryObjectClass
        self.reverseObjectClassMap[cls.primaryObjectClass] = cls.schema.name

        ramap = {}
        for k in cls.attributeMap.keys():
            ramap[cls.attributeMap[k]] = k
        cls.reverseAttributeMap = ramap

    def activate(self):
        """
        Called when the Bundle is activated.

        Register the schema description to the SchemaManager
        """        
        SchemaManager.defaultManager().registerSchema(self)
