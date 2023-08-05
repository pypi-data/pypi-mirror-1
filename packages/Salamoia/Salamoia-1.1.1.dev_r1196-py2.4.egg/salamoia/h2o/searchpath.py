import os
import pathelp
import fnmatch

__all__ = ['SearchPath']

class SearchPath(object):
    """
    This class allows you to quickly find the first matching file inside a search path.    

    Just pass a list of paths to the constructor:

    s = SearchPath(['/tmp', '/usr/share/'])
    s.find()
    """

    def __init__(self, paths):
        """
        """

        self.paths = paths
        if not isinstance(self.paths, list):
            self.paths = [self.paths]
        self.paths = [pathelp.path(p) for p in self.paths]

    def find(self, file):
        """
        Find the first occurrence of 'file' existing in one of the paths
        """

        for p in self.paths:
            if os.path.exists(p / file):
                return p / file
        return None

    def allFiles(self, pattern=None):
        """
        Return all files matching the optional shell pattern.
        """

        res = []
        if not pattern:
            pattern = "*"
        for p in self.paths:
            dir = os.listdir(p)
            res.extend([p/d for d in fnmatch.filter(dir, pattern)])
        return res

    def __repr__(self):
        return ':'.join(self.paths)
