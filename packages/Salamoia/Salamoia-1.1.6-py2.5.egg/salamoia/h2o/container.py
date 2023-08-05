from salamoia.h2o.object import Object

class ObjectContainer(Object):
    """
    This object is used to contain objects that are not
    subclasses of h2o.Object because you may not transfer them
    through the xmlrpc connection without Object magic....
    For example you can not transfer a list of Object-s but
    you must wrap a Container around the list because the root of
    the graph must be a subclass of Object (TODO: fix that)

    OBSOLETE
    """
    def __init__(self, value):
        Object.__init__(self, "")
        self.value = value
        
    def resurrect(self):
        #Ione.log("RESURRECTING container")
        return self.value

Container = ObjectContainer

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
