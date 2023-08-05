

__all__ = ['Attribute']

class Attribute(object):
    """
    An Attribute object carries the attribute name, value, type triplet,
    and is stored inside a hidden dictionary of an h2o.object.Object.

    Attribute values can have different string rappresentation depending
    on if it is meant for displaying to the user or storing in the repository.

    The Type object knows how to display the object and how to store it.
    """
    
    def __init__(self, name, value, type):
        self.special = False
        self.type = type

        self.name = name
        self.value = value

    def display(self):
        """
        helper method. calls Type.displayFormat()
        """
        return self.type.displayFormat(self)

    def store(self):
        """
        helper method calls Type.storeFormat()
        """
        return self.type.storeFormat(self)

    def transportRead(self):
        """
        read for transport (binary data, etc)
        """
        return self.type.transportFormat(self)

    def junkCheck(self):
	return self.type.junkCheck(self.value)
    
    def __str__(self):
        return self.display()

    def __repr__(self):
        return "Attribute(%s)" % (self.display())

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
