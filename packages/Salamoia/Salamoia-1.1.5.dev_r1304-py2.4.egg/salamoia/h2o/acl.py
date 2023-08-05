from salamoia.h2o.decorators import abstract
from salamoia.h2o.exception  import BadAceFormatException
from salamoia.h2o.logioni    import Ione
from salamoia.h2o.generics   import Each

class ACL(list):
    """
    Access control list.

    Will provide a system of fine grained server controlled access.

    TODO: finish implementation
    """

    def __init__(self):
        super(ACL, self).__init__(self)
        #self.append(ACE("a:uid=cojote,ou=People,o=sottosale.net:a"))
        #self.append(ACE("a:uid=marko,ou=People,o=sottosale.net:a"))
        #self.append(ACE("a:uid=mille,ou=People,o=sottosale.net:a"))
        #self.append(ACE("a:uid=phasa,ou=People,o=sottosale.net:a"))
    
    def check(self, id, action):
        for i in self:
            if i.match(id):
                return i.check(action)
        return False

class ACE(object):
    """
    An access control entry.
    An element of the access control list.

    Each ACE is associated with a 'principal' (user or group)

    An ACE has a list of actions (read, write, delete, admin) which state what is the possible action
    the user matching this ace can do with an object
    """
    def __new__(cls, *args):
        if cls == ACE:
            return cls.fromString(args[0])
        return apply(super(ACE, cls).__new__, [cls]+list(args)) # TODO find a cleaner
    
    @classmethod
    def fromString(cls, string):
        """
        Returns a new ACE object parsing the format:
        type:principal:actionlist
        """

        tokens = string.split(':')
        if len(tokens) != 3:
            raise BadAceFormatException, "Bad formatted ace!"
        actions = [Action(x) for x in tokens[2]]
        typeMap = {'a': AllowACE, 'd': DenyACE}
        if not typeMap.has_key(tokens[0]):
            raise BadAceFormatException, "Bad ACE type"

        return typeMap[tokens[0]](tokens[1], actions)
    
    def __init__(self, *args):        
        if len(args) != 2:
            return None
        self.id = str(args[0]).lower()
        self.actions = args[1]

    @abstract
    def _defaultResult(self):
        """
        """

    def match(self, id):
        """
        currently is compares case insensitive, because some
        components of the DN are case insensitive (but others, like username can be case sensitive!)::

          >>> ace = ACE.fromString('a:uid=piPpo,o=SuffiX:rw')
          >>> ace.match('uid=pippo,o=suffix')
          True

        It handles the space between components and '='::

          >>> ace.match('uid =pippo, o=suffix')
          True
          
        But not inside attributes::

          >>> ace.match('uid = pip po, o = suffix')
          False

        """
        normalized = ','.join(Each(id.lower().split(',')).strip())
        normalized = '='.join(Each(normalized.split('=')).strip())
        return self.id == normalized

    def check(self, action):
        for i in self.actions:
            if i.can(action):
                return self._defaultResult()
        return not self._defaultResult()

    def __repr__(self):
        return "%s:%s:%s" % (self.shortName(), self.id, ''.join([str(a) for a in self.actions]))

    def __str__(self):
        return "%s:%s:%s" % (self.shortName(), self.polishId(),
                             ''.join([str(a) for a in self.actions]))

    def polishId(self):
        if self.id.startswith('uid='):
            return self.id.split(',')[0].split('=')[1]
        return self.id
            
class AllowACE(ACE):
    def _defaultResult(self):
        return True
    
    def shortName(self):
        return 'a'
                
class DenyACE(ACE):
    def _defaultResult(self):
        return False
    
    def shortName(self):
        return 'd'

class Action(object):
    """
    An acl Action specifies how a particular acces will be granted
    """
    typeMap = {}
    
    def __new__(cls, *type):
        if cls == Action:
            return cls.fromString(type[0])
        else:
            return super(Action, cls).__new__(cls)

    @classmethod
    def fromString(cls, type):
        if not cls.typeMap:
            cls.typeMap = {'r': ReadAction,
                           'w': WriteAction,
                           'd': DeleteAction,
                           'a': AdminAction}
            
        if not cls.typeMap.has_key(type):
            raise BadAceFormatException, "Bad ACE action type"
        return cls.typeMap[type]()

    def __repr__(self):
        for i in self.typeMap:
            if self.typeMap[i]  == self.__class__:
                return i
        return str(self.__class__).split("'")[1].split(".")[-1]

    def can(self, action):
        return isinstance(self, action.__class__)

class ReadAction(Action):
    pass

class WriteAction(Action):
    pass

class DeleteAction(Action):
    pass

class AdminAction(ReadAction, WriteAction, DeleteAction):
    pass

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
