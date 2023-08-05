import connection

class User:
    _group = None
    
    def __init__(self, dict):
        self.uid = dict['uid'][0]
        self.uidNumber = dict['uidNumber'][0]
        self.gidNumber = dict['gidNumber'][0]
        self.home = dict['homeDirectory'][0]

    def __repr__(self):
        return '<user: %s:%s %s>' % (self.uid, self.group().name, self.home)

    def group(self):
        if not self._group:
            self._group = connection.DefaultConnection().groupByGid(self.gidNumber)
        return self._group

class Group:    
    def __init__(self, dict):
        self.name = dict['cn'][0]

    def __repr__(self):
        return '<group: %s>' % (self.name)


