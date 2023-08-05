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

    Can be used to add backend specific methods to the searchparser and similar.

    It cannot be used if the class has already a metaclass.

    It is used like that:

    >>> class A(object):
    ...   def __init__(self):
    ...      pass
    ...
    ...   def base(self):
    ...      return "base method"

    >>> class B(ClassExtension, A):
    ...   def pippo(self):
    ...      return "pippo"

    >>> a = A()
    >>> a.pippo()
    'pippo'
    """

    __metaclass__ = ClassExtensionMetaclass



# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
