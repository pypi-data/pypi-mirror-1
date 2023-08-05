import sys,os
import ldap,ldapurl

from account import *

suffix = "o=sottosale.net"
protocol = "ldap"
host = "hostello.sottosale.net"

class Connection:    
    peopleSuffix = "ou=People,"+suffix
    groupSuffix = "ou=Group,"+suffix

    def __init__(self):
        self.ldap_url = ldapurl.LDAPUrl(protocol+"://"+host+"/"+suffix)
        self.ldap_url.applyDefaults({
            'who':'',
            'cred':'',
            'scope':ldap.SCOPE_SUBTREE
            })

        self.conn = ldap.ldapobject.ReconnectLDAPObject(self.ldap_url.initializeUrl())
        self.conn.protocol_version = ldap.VERSION3


        self.conn.simple_bind_s(self.ldap_url.who, self.ldap_url.cred)

    def search(self, filter, suf=suffix):
        return self.conn.search_s(suf, self.ldap_url.scope, filter)

    def allUsers(self):
        return map(lambda x: User(x[1]), self.search('(uid=*)', self.peopleSuffix))

    def allGroups(self):
        return map(lambda x: Group(x[1]), self.search('(cn=*)', self.groupSuffix))

    def user(self, name):
        return User(self.search('(uid=%s)' % (name), self.peopleSuffix)[0][1])

    def group(self, name):
        return Group(self.search('(cn=%s)' % (name), self.groupSuffix)[0][1])

    def userByUid(self, uid):
        return User(self.search('(uidNumber=%s)' % (uid), self.peopleSuffix)[0][1])

    def groupByGid(self, gid):
        return Group(self.search('(gidNumber=%s)' % (gid), self.groupSuffix)[0][1])


_defaultConnection = None
def DefaultConnection():
    global _defaultConnection
    if not _defaultConnection:
        _defaultConnection = Connection()
    return _defaultConnection
