from salamoia.h2o.decorators import lazymethod
from salamoia.h2o.logioni    import Ione
from salamoia.h2o.exception  import ConnectionError, EmptyPasswordError
from salamoia.h2o.config     import Config

import ldap, ldapurl

__all__ = ['Connection']

class Connection:
    """
    The connection object abstracts a ldap connection
    and the operation with it.

    It handles the details about host address, passwords etc
    reading the configuration file.

    There is one global connection class, and the connection
    is persistent during the whole lifetime of the server.
    """


    # those are only defaults. real values are read from the config file !
    suffix = "o=default-suffix"
    protocol = "ldap"
    host = "localhost"
    port = 389
    rootDN = "cn=manager"
    rootDNPassword = "secret"

    @classmethod
    @lazymethod
    def defaultConnection(cls):
        """
        Lazy instantiation of the global connection class.

        TODO: move the configuration fetching away from here
        """        

        try:
            cfg = Config()

            cls.suffix = cfg.get('ldap', "suffix", cls.suffix)
            cls.rootDN = cfg.get('ldap', "rootDN", cls.rootDN+","+cls.suffix)
            cls.rootDNPassword = cfg.get('ldap', "rootDNPassword", cls.rootDNPassword)
            cls.host = cfg.get('ldap', "host", cls.host)
            cls.port = cfg.getint('ldap', "port", cls.port)

            return cls(cls.rootDN, cls.rootDNPassword)
        except ConnectionError:
            Ione.log("rootdn bind connection failed")
            raise


    def __init__(self, user='', password=''):
        """
        Initializes the connection creating a ldap.connection object
        and binding it.

        It raises ConnectionError on error
        """
        
        if user and not password:
            raise EmptyPasswordError
        
        self.ldap_url = ldapurl.LDAPUrl(self.protocol+"://"+self.host+"/"+self.suffix)
        self.ldap_url.applyDefaults({
            'who': user,
            'cred': password,
            'scope': ldap.SCOPE_SUBTREE
            })

        self.conn = ldap.ldapobject.ReconnectLDAPObject(self.ldap_url.initializeUrl())
        self.conn.protocol_version = ldap.VERSION3

        try:
            self.conn.simple_bind_s(self.ldap_url.who, self.ldap_url.cred)
        except:
            Ione.log("BIND error...", self.ldap_url)
            raise ConnectionError

    def search(self, filter, base=None, scope=None, attributes=None):
        """
        Search the directory. Basically just a wrapper to provide
        common defaults around 'base' and 'scope'
        """
        if not base:
            base = self.suffix
        if scope is None:
            scope = self.ldap_url.scope
        return self.conn.search_ext_s(base, scope, filter, attrlist=attributes, sizelimit=0)

    def basicModify(self, id, modlist):
        self.conn.modify_s(id, modlist)

    def basicAdd(self, id, modlist):
        self.conn.add_s(id, modlist)

    def basicDelete(self, id):
        self.conn.delete_s(id)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
