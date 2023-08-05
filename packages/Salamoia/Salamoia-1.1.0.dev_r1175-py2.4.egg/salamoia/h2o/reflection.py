import traceback
import sys
from salamoia.h2o.cache import Cache
from salamoia.h2o.logioni import *

class ClassNamed(object):
    """
    Helper class which can return a class object
    from a string and compute a string from the class name
    hiding the difference between old-style and new-style
    python classes.
    """

    namedCache = Cache()
    
    def __new__(cls, name):
        """
        When a ClassNamed object is istantiated
        the real object returned is a the class object
        matching the argument.

        ClassNamed('h2o.user.User')(arg1, arg2, arg3)

        returns a User object construted with arg1, arg2, arg3
        arguments
        """
        if name not in cls.namedCache:
            #Ione.log("ClassNamed cache miss", name)
            c = cls._findClass(name)
            cls.namedCache[name] = c
            return c
        return cls.namedCache[name]
    

    def _findClass(cls, name):
        name = cls.classFullName(name)
        
        modulePath = name.split('.')
        moduleName =  '.'.join(modulePath[0:-1])
        className = modulePath[-1]
        
        if moduleName:
            __import__(moduleName)
            return getattr(sys.modules[moduleName], className)
        else:
            return getattr(sys.modules['__builtin__'], className)

    _findClass = classmethod(_findClass)

    def classFullName(self, cls):
        """
        return the class name from a class hiding the
        difference between old-style and new-style python classes.

        the class full name is composed of it's package and
        module name.
        """
        name = str(cls)
        if name.startswith('<class'): # new style class
            name = name.split("'")[1]
        return name

    classFullName = classmethod(classFullName)

    def className(self, cls):
        """
        return only the class name, stripping all package and module
        information
        """
        full = self.classFullName(cls)
        return full.split(".")[-1]
        
    className = classmethod(className)
    
class ClassExtender(object):
    """
    This class helps conditional class redirection.
    It features a register of class->class mappings grouped
    with a key (usally another class but can be anything)
    Changing this defaultGroup key the mapping can be changed easly.
    Users of this class will probably want to call 'new' inside their
    '__new__' in the generic class and call 'registerClassRedirect'
    inside the body of the class's module
    """
    
    registry = {}
    inverseRegistry = {}
    defaultGroup = ""

    namedCache = Cache()
    
    def registerClassRedirect(cls, original, redirection, group=None):
        if not group:
            group = cls.defaultGroup

        if not cls.registry.has_key(group):
            cls.registry[group] = {}
            cls.inverseRegistry[group] = {}
            
        cls.registry[group][original] = redirection
        cls.inverseRegistry[group][redirection] = original

    registerClassRedirect = classmethod(registerClassRedirect)

    def classRedirect(cls, original, group=None):
        if not group:
            group = cls.defaultGroup            
        try:
            return cls.registry[group][original]
        except:
            return original

    classRedirect = classmethod(classRedirect)

    def classRedirectNamed(cls, name):
        return cls.classRedirect(ClassNamed(name))

    classRedirectNamed = classmethod(classRedirectNamed)

    def inverseClassRedirect(cls, original, group=None):
        if not group:
            group = cls.defaultGroup
        try:
            return cls.inverseRegistry[group][original]
        except:
            return original

    inverseClassRedirect = classmethod(inverseClassRedirect)
    
    def new(cls, superClass, targetClass, args):
        """
        Call this from your '__new__' and your class with automatically transmute
        with the mapping set with 'registerClassRedirect'
        """
        realClass = cls.classRedirect(targetClass)
        return apply(superClass.__new__, [realClass]+list(args))

    new = classmethod(new)
