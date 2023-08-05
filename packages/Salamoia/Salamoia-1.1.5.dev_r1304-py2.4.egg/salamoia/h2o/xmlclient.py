import xmlrpclib
from salamoia.h2o.logioni import *
from salamoia.h2o.protocols import NO_ADAPTER_NEEDED
import traceback

import base64, urllib, string, sre

class ClientCredentialsMetaclass(type):
    def __init__(cls, name, bases, dict):
        super(ClientCredentialsMetaclass, cls).__init__(name, bases, dict)

        if hasattr(cls, 'methodName'):
            cls.methodMap[cls.methodName] = cls


class ClientCredentials(object):
    __metaclass__ = ClientCredentialsMetaclass
    
    methodMap = {}
    
    def encode(self):
        raise NotImplementedError

    @classmethod
    def authenticateWithMethod(cls, method, base, username, password, headers):
        cred = cls.methodMap.get(method)
        if cred:
            return cred.authenticate(base, username, password, headers)
        return False

    @classmethod
    def authenticate(cls, base, username, password, headers):
        credentials = cls.authenticationCredentials(base, username, password, headers)
        proxy = Proxy(base=base, credentials=credentials)
        try:
            proxy.connectionAuthenticationCheck()
            print "Authenticated using", cls.methodName
            return credentials
        except xmlrpclib.ProtocolError, error:
            #print cls.methodName, "auth error"
            pass

        return None

class BasicClientCredentials(ClientCredentials):
    methodName = "Basic"
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def encode(self):
        auth = base64.encodestring(urllib.unquote("%s:%s" % (self.username, self.password)))
        auth = string.join(string.split(auth), "") # get rid of whitespace
        return "Basic " + auth

    @classmethod
    def authenticationCredentials(cls, base, username, password, headers):
        return cls(username, password)

class TokenClientCredentials(ClientCredentials):
    def __init__(self, token):
        self.token = token

    def encode(self):
        auth = self.token
        auth = string.join(string.split(auth), "") # get rid of whitespace
        return "Token " + auth

class SSHClientCredentials(TokenClientCredentials):
    methodName = "SSH"
    
    @classmethod
    def authenticationCredentials(cls, base, username, password, headers):
        from Crypto.Util.randpool import RandomPool
        import paramiko, base64
        import urlparse

        baseRoot = urlparse.urljoin(base, '/')               

        ch = headers['challenge']
        key = paramiko.Agent().get_keys()[0]
        sig = base64.encodestring(key.sign_ssh_data(RandomPool(), ch)).replace("\n","")

        proxy = Proxy(base=baseRoot, credentials=BasicClientCredentials('anonymous', 'unauthenticated'))

        if '@' not in username:
            username = username + "@" + headers['realm']
        proxy.authmanager.ssh.response(username, ch, sig)
        return cls(sig)

class Transport(xmlrpclib.Transport):
    user_agent = "Salamoia xmlrpc"

    def __init__(self, proxy):
        self.proxy = proxy

    def get_host_info(self, host):
        host, extra_headers, x509 = xmlrpclib.Transport.get_host_info(self, host)

        if self.proxy._credentials:
            extra_headers = [
                ("Authorization", self.proxy._credentials.encode())
                ]

        return host, extra_headers, x509
        

class Proxy(object):
    def __init__(self, name='', base='', parent=None, interfacePair=None, credentials=None):
        self._name = name
        self._base = base
        self._parent = parent

        if parent:
            self._interfacePair = parent._interfacePair
            self._credentials = parent._credentials
        else:
            if interfacePair is None:
                interfacePair = (NO_ADAPTER_NEEDED, NO_ADAPTER_NEEDED)
            self._interfacePair = interfacePair
            self._credentials = credentials

    def __getattr__(self, name):
        if name == '_connection':
            self._connection = xmlrpclib.Server(self._base, allow_none=True, transport=Transport(self))
            return self._connection
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError, "no such attribute"

        return Proxy(name, self._base + '/' + name, self)

    def __call__(self, *args):
        res = getattr(self._parent._connection, self._name)(*(self._interfacePair[0](args)))

        return self._interfacePair[1](res)


class Client(Proxy):
    """
    Compatibility interface
    """

    def __init__(self, host, port, timeout=-1.0, username=None, password=None, base="hostello", interfacePair=None):
        base = "http://%s:%s/%s" % (host, port, base)

        def explode(header):
            method, args = header.split(" ")
            args = dict([sre.match('(.*)="(.*)"', x).groups() for x in args.split(',')])
            
            return method, args

        headers = {}
        proxy = Proxy(base=base)
        try:
            proxy.connectionAuthenticationCheck()
        except xmlrpclib.ProtocolError, error:
            headers = dict([explode(h) for h in error.headers.getheaders("WWW-Authenticate")])

        methods = headers.keys()
        orderedMethods = ['SSH', 'GSSAPI', 'Basic']
        methods.sort(lambda x, y: cmp(orderedMethods.index(x), orderedMethods.index(y)))

        for m in methods:
            credentials = ClientCredentials.authenticateWithMethod(m,
                                                                   base,
                                                                   username, password,
                                                                   headers[m])
            if credentials:
                break 
                
        super(Client, self).__init__(base=base, interfacePair=interfacePair, credentials=credentials)

        # credentials can be null if no authentication method is configured. In this case we must
        # check if anonymous authentication is accepted because this constructor is expected raise an exception
        # if the server doesn't authenticate        
        if not credentials:
            self.connectionAuthenticationCheck()
                
