__all__ = ['ClassExtension']

def _func():
    pass

class ClassExtensionMetaclass(type):
    """
    This metaclass is the machinery that make ClassExtension work
    """
    def __init__(cls, name, bases, dict):
        if name == "ClassExtension":
            return

        base = bases[1]
        for i in dict:
            if isinstance(dict[i], type(_func)) or isinstance(dict[i], classmethod) or isinstance(dict[i], staticmethod):
                setattr(base, i, dict[i])

class ClassExtension(object):
    """
    With this class we can add methods to an already defined class.

    Can be used to add backend specific methods to the searchparser and similar

    It is used like that:

    class A(object):
      def __init__(self):
         print "init a"

      def base(self):
         print "base method"

    class B(ClassExtension, A):
      def pippo(self):
         print "pippo"

    a = A()
    a.pippo()

    """

    __metaclass__ = ClassExtensionMetaclass


