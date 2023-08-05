import base64, string
import md5, sha
from random import choice
from salamoia.h2o.logioni import *

class PasswordHasher(object):
    def __init__(self, password):
        self.password = password

    #def encode(self, algo='SHA'):
    #    return 

    def hash(self, algo='SHA'):

        salt = ''
        password = self.password

        if algo == 'CLEARTEXT':
            return self.password
        
        if 'SHA' in algo:
            module = sha
        elif 'MD5' in algo:
            module = md5
        else:
            raise "unsupported encryption"

        if algo == 'SSHA' or algo == 'SMD5':
            for i in range(0,4):
                salt += choice(string.ascii_letters + string.digits)
            password += salt

	if type(password) == list:
	    Ione.log("PASSSWORD '%s' e' lista" % (password))
        return '{%s}%s' % (algo, base64.encodestring(module.new(password).digest() + salt))
