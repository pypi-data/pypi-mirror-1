"""
"""

from salamoia.h2o import search as hs
from salamoia.h2o.search import *

from sets import Set

from salamoia.h2o.decorators import *
from salamoia.h2o.protocols import advise, Adapter, ContextualInterface, DelegatingContextualAdapter, contextualAdapt
from salamoia.h2o.logioni import Ione

import ldap

class ILdapSearch(ContextualInterface):
    """
    """

    def filter():
        """
        """

    def setServiceContext(service):
        """
        """

    def needTrimming():
        """
        """

    def findSpecClass(cls):
        """
        """

class Common(DelegatingContextualAdapter(ILdapSearch)):
    """
    Baseclass for other adapters, just delegates the common methods to the subject

    TODO: move to h2o.
    TODO: find a compact hash and cmp without filter and stable
    """

    def __cmp__(self, other):
        return self.filter().__cmp__(other.filter())

    def __hash__(self):
        return self.filter().__hash__()

class TypeSpec(Common):
    """
    The ldap type specification maps generic
    salamoia type names to ldap specific object
    class names.

    The TypeSpec class will map these 'type' names
    to real class names.
    """

    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.TypeSpec])

    def objectClass(self):
        schema = self.service.serviceDescription.schema
        return schema.objectClassMap[self.type]

    @classmethod
    def fromObjectClass(cls, classes, service):
        """
        This is a class method.

        It returns an instance of this class
        with the type matching the any value of "classes"

        The 'classes' argument can also be a single string.

        The service parameter is needed to access service specific namespace
        """
        if not isinstance(classes, list):
            classes = [classes]

        schema = service.serviceDescription.schema

        for i in classes:
            if schema.reverseObjectClassMap.has_key(i):
                res = hs.TypeSpec(schema.reverseObjectClassMap[i])
                res.service = service
                return res
        return None
        
    def filter(self):
        """
        it generates the filter needed to univoquely identify
        the the object given it's objectclass.
        """
        return "(objectclass=%s)" % (self.objectClass())
    
class PropSpec(Common):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.PropSpec])

    def filter(self):
        """
        Property 
        """

        definitions = self.context.definitions.values()
        mappings = reduce(lambda x,y: x.extend(y) or x, [x.ldap.mappings for x in definitions], [])

        close = "%s%s" % (self.op, self.val)

        alternate = ["(&(objectclass=%s)(%s))" % (x.parent.objectClasses.structural, x.ldap + close) 
                     for x in mappings if x.name == self.prop]
    
        filter = "".join(alternate)

        #test = [x for x in mappings if x.name == self.prop]
        #Ione.warning("FILTER PROP", self.prop, test, [x.name for x in test], [x.parent.objectClasses.structural for x in test])
        
        # simple filter simple debug
        if len(alternate) == 0:
            return "(%s=%s)" % (self.prop, self.val)
        elif len(alternate) == 1:
            return filter
        return "(|" + filter + ")"

class OwnerSpec(Common):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.OwnerSpec])

    def filter(self):
        """
        Uses an extended DN search.
        This way the filter is a valid ldap filter.

        The old way was to do a base search hooked on the owner ID
        which is probably a little faster but this way the search
        can be entierly specified with a ldap filter alone and no
        'tricks' defined in ldapbackend.py
    
        """
        components = [x.split('=') for x in self.owner.split(',') if x.split('=')[0] != 'ou'] # remove bugged 'ou' slapd < 2.3.x
        #components = [x.split('=') for x in self.owner.split(',') ]
        filters = ['(%s:dn:=%s)' % (x, y) for x,y in components]
        return '(&%s)' % (''.join(filters))

class SubOwnerSpec(Common):
    """
    This is peculiar because it does a subfetch.
    It uses self.service as service. It is set recursively using setServiceContext
    """
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.SubOwnerSpec])

    def filter(self):
        res =  self.service.search(self.expr)
        
        o = hs.OwnerSpec('')
        filters = []
        for r in res:
            o.owner = r
            filters.append(contextualAdapt(o, ILdapSearch, self.context).filter())
        return '(|%s)' % (''.join(filters))

class NullSpec(Common):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.NullSpec])

    def filter(self):
        return ""

class AnySpec(Common):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.AnySpec])
    
    def filter(self):
        return "objectclass=*"

class CompositeSpec(Common):
    """
    The class redirection alchemy works well but it doesn't work with
    superclasses.

    For this reasions ldap subclasses of CompositeSpec should
    have a multiple inheritance giving explicitly LDAPCompositeSpec
    in their superclass list.
    """
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.CompositeSpec])

    def filter(self):
        return "(%s%s)" % (self.operatorName(),
                           ''.join([contextualAdapt(x, ILdapSearch, self.context).filter() for x in self.children]))

class AndSpec(CompositeSpec):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.AndSpec])

    def trim(self, selectedObjects):
        res = Set(selectedObjects)
        for i in self.children:
            res = res.intersection(i.trim(list(res)))
            seed = res

        return list(res)

class OrSpec(CompositeSpec):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.OrSpec])

    def trim(self, selectedObjects):
        res = Set()
        for i in self.children:
            res = res.union(i.trim(selectedObjects))
        return list(res)

class NotSpec(CompositeSpec):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.NotSpec])

    def trim(self, selectedObjects):
        res = Set(selectedObjects)
        for i in self.children:
            res = res.difference(i.trim(selectedObjects))
        return list(res)

class AggregateSpec(Common):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.AggregateSpec])

    def filter(self):
        return "(%s=*)" % (self.attribute)

    def trim(self, selectedObjects):
        raise NotImplementedError, "to be overriden"

    def needTrimming(self):
        return True

class MaxSpec(AggregateSpec):
    """
    values must be integers
    """
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.MaxSpec])

    def trim(self, selectedObjects):
        res = None
        max = 0;

        if not selectedObjects:
            return []

        for i in selectedObjects:
            value = int(getattr(i, self.attribute))
            if value > max:
                max = value
                res = i
        return [res]

class BaseSpec(CompositeSpec):
    advise(instancesProvide=[ILdapSearch],
           asAdapterForTypes=[hs.BaseSpec])

    def filter(self):
        return contextualAdapt(self.children[0], ILdapSearch, self.context).filter()

    def scope(self):
        if self._scope == "base":
            return ldap.SCOPE_BASE
        elif self._scope == "sub":
            return ldap.SCOPE_SUBTREE
        elif self._scope == "one":
            return ldap.SCOPE_ONELEVEL

                
    def base(self):
        return self._base

    def trim(self, selectedObjects):
        return self.children[0].trim(selectedObjects)
    

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
