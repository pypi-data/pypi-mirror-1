class Mixin(object):
    """
    Inheriting from this class allows the subclass to insert itself int the ancestor list of another class
    """

    @classmethod
    def mixIn(cls, dest):
        if not cls in dest.__bases__:
            dest.__bases__ = tuple(list(dest.__bases__) + [cls])


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
