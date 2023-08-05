import shelve 
import os

class TemplateEngine(object):

    def __init__(self, varPath, filename="Templates.db"):
	self.myInfo = []
	self.filename = os.path.join(varPath, filename)

    def list(self):
	try:
	    data = shelve.open(self.filename)
	except:
	    raise "Db not found"
	keys = data.keys()
	data.close() 
#	Ione.log("In TemplateEngine List:", self, keys)
	return keys


    def add(self, key, thing):
	try:
	    data = shelve.open(self.filename)
	except:
	    raise  "File not found"
	if data.has_key(key):
	    data[key] = thing
	    data.close()	
	else: 
	    data[key] = thing
	    data.close()
#	Ione.log("In TemplateEngine Add:", self)
	    
    def get(self,key):
	data = shelve.open(self.filename)
	if data.has_key(key):
	    ret = data[key]
	    data.close()
#	    Ione.log("In TemplateEngine get:", self, ret)
	    return ret
        else:
	    return None


    def pop(self,key):
	data = shelve.open(self.filename)
	if data.has_key(key):
	    ret = data.pop(key)
	    data.close()
#	    Ione.log("In TemplateEngine pop:", ret)
	    return ret
        else:
	    return None

    def __repr__(self):
	return "<%s:filename=%s>" % (self.__class__.__name__, self.filename )


    

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
