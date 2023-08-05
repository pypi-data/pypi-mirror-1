from salamoia.h2o.type import *

class LDAPPasswordType(PasswordType):
    pass

ClassExtender.registerClassRedirect(PasswordType, LDAPPasswordType, "salamoia.macina.ldap.ldapbackend.LDAPBackend")
