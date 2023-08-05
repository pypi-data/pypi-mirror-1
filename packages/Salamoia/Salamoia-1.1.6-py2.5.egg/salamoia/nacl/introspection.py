from salamoia.h2o.logioni import Ione

from inspect import ismethod
from sets import Set

class IntrospectionControl(object):
    def _publicMethods(self):
        return [getattr(self, x) for x in dir(self) if x[0] != '_' and ismethod(getattr(self, x))]
    
    def listMethods(self):
        """
        List of public method names exported by this service
        """
        return [x.__name__ for x in self._publicMethods()]

    def methodHelp(self, name):
        """
        Returns the doc string of the named method. If the method is
        implemented in various superclasses, each superclass implementation
        is returned.

        The result is a dictionary with class names as keys and docstrings as values
        """
        
        if name[0] == "_":
            return ""

        docs = {}
        for c in self.__class__.__mro__:
            method = c.__dict__.get(name)
            if method and method.__doc__ and method.__doc__ not in docs.values():
                docs[c.__name__] = method.__doc__
                
        return docs
        
        
    
