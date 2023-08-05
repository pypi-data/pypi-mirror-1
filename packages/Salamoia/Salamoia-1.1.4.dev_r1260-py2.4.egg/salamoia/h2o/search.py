from salamoia.h2o.object     import Object
from salamoia.h2o.decorators import abstract

class SearchSpecification(Object):
    def findSpecClass(self, cls):
        """
        Searches through the serach specification tree an object
        matchin the class 'cls'.
        """
        if isinstance(self, cls):
            return self
        return None

    def setServiceContext(self, service):
        """
        Link a service to this particular tree of search specifications.

        Used to access to service specific namespace (for example schema objectclasses etc)
        """
        self.service = service

    def trim(self, selectedObjects):
        """
        further trim the selected objectes with nacl-side operations
        """
        return selectedObjects

    def needTrimming(self):
        """
        Return true in a subclass otherwise the trim operation will be skipped    
        """
        return False

    def __cmp__(self, other):
        return self.filter().__cmp__(other.filter())

    def __hash__(self):
        return self.filter().__hash__()

    def scope(self):
        """
        ldap help method
        """
        return None

    def base(self):
        """
        ldap help method
        """
        return None

    @abstract
    def setScope(self, scope):
        """
        Set the scope
        """

    @abstract
    def setBase(self, base):
        """
        Set the base
        """

class TypeSpec(SearchSpecification):
    """
    Type spec searches an object of a specified type.
    
    Type names are kept generic, but mapped one-to-one
    with python classes, and backend specific names (see LDAPTypeSpec).

    This allows to have a common and firm nomenclature while
    specific implementation can change and evolve.
    
    """

    # TODO: build dynamically
    allowedChildrenMap = {'user': ['mail', 'domain', 'virtualhost','database'],
                          'group': [],
                          'mail': [],
                          'domain': [],
                          'virtualhost': [],
                          'database': []}
    
    
    def __init__(self, type):
        self.type = type

    def toClass(self):
        """
        Converts a type to a python class
        """
        return self.service.serviceDescription.schema.classMap[self.type]

    def allowedChildren(self):
        """
        Returns a list of the types that can be children
        of this object.

        (Used for example in salamoia.ashella.vfs 
        """
        return self.allowedChildrenMap[self.type]
    
    def __repr__(self):
        return "<type>=%s" % (self.type)

class PropSpec(SearchSpecification):
    """
    This is a generc attribute match specification.
    
    TODO: Attribute names will get eventually a translation here
    when other backends are implemented. now they match object instance
    variables and backend attributes    

    TODO: why it's called property when all over we use 'attribute'?
    """
    def __init__(self, prop, val, op='='):
        self.prop = prop
        self.val = val
        self.op = op

    def __repr__(self):
        return "%s%s%s" % (self.prop, self.op, self.val)

class MultiPropSpec(SearchSpecification):
    """
    This is a generc attribute match specification.
    """
    def __new__(self, AttrsList, type):
	return type([ PropSpec(x,y) for x,y in AttrsList])
    
class AnySpec(SearchSpecification):
    """
    objectclass=*
    """

    def __repr__(self):
        return "any"

class NullSpec(SearchSpecification):
    def __repr__(self):
        return '<null>'

class OwnerSpec(SearchSpecification):
    """
    The main difference of this specification is that whenever it is located
    it doesn't respect logic constrains (TODO maybe).
    So even if it is inside a NotSpec it doesn't negate.
     Theoretically it should be included in a top level AndSpec, but this is not
    enforced yet.
    """
    def __init__(self, owner):
        self.owner = owner

    def __repr__(self):
        return "<owner>=%s" % (self.owner)

class SubOwnerSpec(SearchSpecification):
    """
    This one allows to specify the owner with a subexpression
    """
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "<subowner>=%s" % (self.expr)

class CompositeSpec(SearchSpecification):
    """
    A composite specification glues together other specification
    with logical rules (and, or, not).
    """
    
    def __init__(self, children):
        self.children = children

    def add(self, obj):
        self.children.append(obj)

    def __repr__(self):
        return "(%s%s)" % (self.operatorName(),
                           "".join(["(%s)" % (str(x)) for x in self.children]))

    def operatorName(self):
        raise NotImplementedError, 'must override'

    def findSpecClass(self, cls):
        """
        iterates through children. see SearchSpecification.findSpecClass
        """
        for i in self.children:
            res = i.findSpecClass(cls)
            if res:
                return res
        return None

    def setServiceContext(self, service):
        """
        Propagate the service to children
        """
        self.service = service
        for i in self.children:
            i.setServiceContext(service)

    def containsSpecClass(self, cls):
        """
        if this container directly contains
        an object of the specified class return it.
        otherwise return none
        """
        for i in self.children:
            if isinstance(i, cls):
                return i
        return None

    def needTrimming(self):
        """
        iterates through children. see SearchSpecification.needTrimming
        """
        for i in self.children:
            if i.needTrimming():
                return True
        return False

class AndSpec(CompositeSpec):
    def operatorName(self):
        return "&"

class OrSpec(CompositeSpec):
    def operatorName(self):
        return "|"

class NotSpec(CompositeSpec):
    def __init__(self, children):
        if len(children) > 1:
            raise "NotSpec cannot contain a list of more than one object"
        super(NotSpec, self).__init__(children)

    def operatorName(self):
        return "!"

class AggregateSpec(SearchSpecification):
    """
    An aggregate (name borrowed from SQL) specification
    selects one entry which fulfills an expression on an attribute
    of the selected subset of objects.
    """
    def __init__(self, attribute):
        self.attribute = attribute
    

class MaxSpec(AggregateSpec):
    def __repr__(self):
        return "(max(%s))" % (self.attribute)

class BaseSpec(CompositeSpec):
    def __init__(self, child, scope, base):
        super(BaseSpec, self).__init__([child])
        self._scope = scope
        self._base = base

    def __repr__(self):
        return "%s@%s;%s" % (self.children[0], self._base, self._scope)

    def setScope(self, scope):
        self._scope = scope

    def setBase(self, base):
        self._base = base

    def scope(self):
        return self._scope

    def base(self):
        return self._base

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
