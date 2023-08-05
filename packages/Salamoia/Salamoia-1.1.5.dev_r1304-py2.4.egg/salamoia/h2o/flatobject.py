from salamoia.h2o.logioni import Ione
from salamoia.h2o.object import Object
import types

class FlatObject(Object):
    _attributeTypeMap = {'acl': types.ACL()}
    
    def __init__(self, ldapres=None):

        if ldapres and (isinstance(ldapres, list) or isinstance(ldapres, tuple)):

            id, attrs = ldapres
            super(FlatObject, self).__init__(id)

            for i in attrs:
                setattr(self, i, attrs[i])
            
            self.id = id
        else:
            super(FlatObject, self).__init__("")
            if ldapres:
                self.merge(ldapres)


    def __setattr__(self, name, value):
        """
        backend doesn't like integer values.
        this method converts integer to string before setting the attribute
        """
        return super(FlatObject, self).__setattr__(name, self._coerceValue(value))

    def __repr__(self):
        return "FlatObject(%s)" % (self.inspectableDict())

    def store(self, mode):
        Ione.log("Storing FLAT Object")

    def inspectableDict(self):
	res = super(FlatObject, self).inspectableDict()
	res["id"] = self.id
        if res.has_key('acl'):
            del res["acl"]
	for i in res.keys():
	    if len(res[i]) == 1:
		res[i] = res[i][0]
	return res

    def merge(self, other):
        if isinstance(other, list):
            for o in other:
                #print "RECURSE into", o
                self.merge(o)
            return

        if hasattr(other, 'inspectableDict'):
            attrs = other.inspectableDict()
        elif hasattr(other, '_usefulAttributes'):
            attrs = other._usefulAttributes()
        else:
            attrs = other.__dict__
        for i in attrs:
            if i == 'id':
                continue
            values = getattr(other, i)
            if not isinstance(values, list):
                values = [values]
            values = [self._coerceValue(v) for v in values]

            if hasattr(self, i):
                if not isinstance(getattr(self, i), list):
                    setattr(self, i, [getattr(self, i)])
                getattr(self, i).extend(values)
            else:
                setattr(self, i, values)
    
    def _coerceValue(self, v):
        if isinstance(v, int):
            return str(v)
        return v

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
