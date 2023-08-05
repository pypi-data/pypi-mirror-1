import os
# funzione d'aiuto

def splitall(path):
    """Split a path into all of its parts.
    
    From: Python Cookbook, Credit: Trent Mick
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

# classe importante

_translate = { '..': os.pardir }
class path(str):
   def __str__(self):
       return os.path.normpath(self)
   def __div__(self, other):
       other = _translate.get(other, other)
       return path(os.path.join(str(self), str(other)))
   def __len__(self):
       return len(splitall(str(self)))
   def __getslice__(self, start, stop):
       parts = splitall(str(self))[start:stop]
       return path(os.path.join(*parts))
   def __getitem__(self, i):
       return path(splitall(str(self))[i])

   def mtime(self):
       return os.path.getmtime(self)

   def exists(self):
       return os.path.exists(self)

   def __add__(self, arg):
       return path(str.__add__(self, arg))

   def fileType(self):
       return self[-1].split(".")[-1]

   def fileName(self):
       return '.'.join(self[-1].split('.')[0:-1])
   
