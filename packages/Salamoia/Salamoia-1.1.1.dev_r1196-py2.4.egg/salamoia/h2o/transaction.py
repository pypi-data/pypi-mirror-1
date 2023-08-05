"""
Probably obsolete module
"""

from object import *

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
