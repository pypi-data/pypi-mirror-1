from salamoia.h2o.lock import ObjectLock
from salamoia.h2o.logioni import *

class LockControl(object):
    def __init__(self):
        Ione.log("LockControl init")
        super(LockControl, self).__init__()

        self.locks = {}

    def lockForEditing(self, id):
        Ione.log("Locking for editing:", id)
        self.locks[id] = ObjectLock(id, self._currentUser)
        return 1

    def unlockForEditing(self, id):
        del self.locks[id]
        return 1;

    def isLockedForEditing(self, id, strict=False):
        Ione.log("Testing lock:", id)

        l = self.locks.get(id)
        if not l:
            return 0
        if l.isExpired():
            Ione.log("Lock expired:", id)
            del self.locks[id]
            return 0

        if not strict:
            if l.owner == self._currentUser:
                Ione.log("Same user:", id, l.owner)
                return 0

        return l
        
    def resetEditingLocks(self):
        Ione.log("Resetting locks on client request")
        self.locks = {}
        return 0
    
    def showEditingLocks(self):
        return repr(self.locks)
