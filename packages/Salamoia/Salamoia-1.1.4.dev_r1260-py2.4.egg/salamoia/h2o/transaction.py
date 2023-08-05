"""
Probably obsolete module
"""

from object import Object
from salamoia.h2o import types

class TransactionProxy(Object):
    """
    No one knows if this is still useful...
    """

    _attributeTypeMap = {'acl': types.ACL()}
    
    def __init__(self, id):
        super(TransactionProxy, self).__init__()
        self.id = id

    def __str__(self):
        return "Transaction(%s)" % (self.id)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
