from salamoia.h2o.logioni import Ione

class SecurityControl(object):
    def getACL(self, *ids):
        res =  [x.acl for x in self.fetch(list(ids))]
        return [[str(ace) for ace in acl] for acl in res]
        
    
