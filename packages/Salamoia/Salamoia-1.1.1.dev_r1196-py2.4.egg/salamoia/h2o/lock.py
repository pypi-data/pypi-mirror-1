from object import *
import time
import datetime

class ObjectLock(Object):
    def __init__(self, obj, owner, timeout=60):
        self.stamp = time.time()
        self.obj = obj
        self.owner = owner
        self.timeout = timeout

    def isExpired(self):
        now = time.time()
        return (now - self.stamp) > self.timeout

    def timeRemaining(self):
        now = time.time()
        return self.timeout - (now - self.stamp) 
