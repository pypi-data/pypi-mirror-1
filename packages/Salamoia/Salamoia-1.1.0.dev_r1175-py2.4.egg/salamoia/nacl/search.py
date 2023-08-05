from salamoia.h2o import search as hs
from salamoia.h2o.search import *

from salamoia.h2o.reflection import ClassExtender
from salamoia.h2o.logioni import Ione
from sets import Set

class TypeSpec(hs.TypeSpec):
    """
    The ldap type specification maps generic
    salamoia type names to ldap specific object
    class names.

    The TypeSpec class will map these 'type' names
    to real class names.
    """
    def objectClass(self):
        return interface.objectClassMap[self.type]

    def fromObjectClass(cls, classes):
        """
        This is a class method.

        It returns an instance of this class
        with the type matching the any value of "classes"

        The 'classes' argument can also be a single string.
        """
        if not isinstance(classes, list):
            classes = [classes]

        for i in classes:
            if interface.reverseObjectClassMap.has_key(i):
                return cls(interface.reverseObjectClassMap[i])
        return None
        
    fromObjectClass = classmethod(fromObjectClass)
        
    def filter(self):
        """
        it generates the filter needed to univoquely identify
        the the object given it's objectclass.
        """
        return "(objectclass=%s)" % (self.objectClass())
    
class PropSpec(hs.PropSpec):
    def filter(self):
        return "(%s=%s)" % (self.prop, self.val)

class OwnerSpec(hs.OwnerSpec):
    def filter(self):
        """
        Uses an extended DN search.
        This way the filter is a valid ldap filter.

        The old way was to do a base search hooked on the owner ID
        which is probably a little faster but this way the search
        can be entierly specified with a ldap filter alone and no
        'tricks' defined in ldapbackend.py
    
        """
        #components = [x.split('=') for x in self.owner.split(',') if x.split('=')[0] != 'ou'] # remove bugged 'ou' slapd < 2.3.x
        components = [x.split('=') for x in self.owner.split(',') ]
        filters = ['(%s:dn:=%s)' % (x, y) for x,y in components]
        return '(&%s)' % (''.join(filters))

class SubOwnerSpec(hs.SubOwnerSpec):
    """
    This is peculiar because it does a subfetch.
    It uses self.backend as backend. It is set recursively using setBackendContext
    """
    def filter(self):
        res =  self.backend.search(self.expr)
        
        o = OwnerSpec('')
        filters = []
        for r in res:
            o.owner = r
            filters.append(o.filter())
        return '(|%s)' % (''.join(filters))

class NullSpec(hs.NullSpec):
    def filter(self):
        return ""

class CompositeSpec(hs.CompositeSpec):
    """
    The class redirection alchemy works well but it doesn't work with
    superclasses.

    For this reasions ldap subclasses of CompositeSpec should
    have a multiple inheritance giving explicitly LDAPCompositeSpec
    in their superclass list.
    """
    def filter(self):
        return "(%s%s)" % (self.operatorName(),
                           ''.join([x.filter() for x in self.children]))

class AndSpec(CompositeSpec, hs.AndSpec):
    def trim(self, selectedObjects):
        res = Set(selectedObjects)
        for i in self.children:
            res = res.intersection(i.trim(list(res)))
            seed = res

        return list(res)

class OrSpec(CompositeSpec, hs.OrSpec):
    def trim(self, selectedObjects):
        res = Set()
        for i in self.children:
            res = res.union(i.trim(selectedObjects))
        return list(res)

class NotSpec(CompositeSpec, hs.NotSpec):
    def trim(self, selectedObjects):
        res = Set(selectedObjects)
        for i in self.children:
            res = res.difference(i.trim(selectedObjects))
        return list(res)

class AggregateSpec(hs.SearchSpecification):
    def filter(self):
        return "(%s=*)" % (self.attribute)

    def trim(self, selectedObjects):
        raise NotImplementedError, "to be overriden"

    def needTrimming(self):
        return True

class MaxSpec(hs.MaxSpec, AggregateSpec):
    """
    values must be integers
    """
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

class BaseSpec(CompositeSpec, hs.BaseSpec):
    def filter(self):
        return self.children[0].filter()

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
    

ClassExtender.registerClassRedirect(hs.TypeSpec, TypeSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.PropSpec, PropSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")

ClassExtender.registerClassRedirect(hs.OwnerSpec, OwnerSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.NullSpec, NullSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.CompositeSpec, CompositeSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.AndSpec, AndSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.OrSpec, OrSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.NotSpec, NotSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.AggregateSpec, AggregateSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.MaxSpec, MaxSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
ClassExtender.registerClassRedirect(hs.BaseSpec, BaseSpec,
                                    "salamoia.nacl.ldap.ldapbackend.LDAPBackend")
