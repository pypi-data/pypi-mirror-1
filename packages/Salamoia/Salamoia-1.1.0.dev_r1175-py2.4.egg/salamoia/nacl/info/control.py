from salamoia.h2o.template import * 
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *
from salamoia.h2o.container  import *
from salamoia.nacl.backend import * 
from salamoia.h2o.logioni import *

class TemplateControlDelegate(object):
    def __init__(self, filename = "Template.db"):
	super(TemplateControlDelegate, self).__init__()	
	varPath =  NACLBackend.defaultBackend().varPath()
	self.engine = TemplateEngine(varPath, filename )
#	Ione.log("TemplateControlDelegated Created:", filename, self.engine )

    def getTemplate(self, name):
	return Container(self.engine.get(name))

    def addTemplate(self, name, info):
	self.engine.add(name, info)
	return 1
    
    def listTemplate(self):
	return self.engine.list()
	
    def popTemplate(self, name):
	return Container(self.engine.pop(name))


class TemplateControl(object):
    def __init__(self, filename = "Template.db"):
	super(TemplateControl, self).__init__()	
	self.delegate = TemplateControlDelegate(filename)
#	Ione.log("TemplateControl Loaded:" )

    def getTemplate(self, *args):
	return self.delegate.getTemplate(*args)
	
    def addTemplate(self, *args):
	return self.delegate.addTemplate(*args)

    def listTemplate(self, *args):
	return self.delegate.listTemplate(*args)

    def popTemplate(self, *args):
	return self.delegate.popTemplate(*args)




######## Storage generic ###################################	


class StorageObject(object):
    
    def __init__(self, filename = "generic.db"):
	super(StorageObject, self).__init__()	
	varPath = NACLBackend.defaultBackend().varPath()
	self.engine = TemplateEngine(varPath, filename )
    
    
    def get(self, name):
	return self.engine.get(name)

    def add(self, name, info):
	self.engine.add(name, info)
	return 1
    
    def list(self):
	return self.engine.list()

    def update(self, name, info):
	obj = self.pop(name)
	self.add(name, info)

    def pop(self, name):
	return self.engine.pop(name)





class StorageOperation(object):
   def  __init__(self):
       pass


class AddOp(StorageOperation):
    def __call__(self, storages, name, element_name, element):
	storage = storages[name][0]
	print storage
	try:
	    storage.add(element_name, element)
	    return 1
	except:
	    raise "Element not added to %s " % name


class ListOp(StorageOperation):

    def __call__(self, storages, name):

	if  storages.has_key(name):
	    return Container(storages[name][0].list())
	else:
	    raise "no such storage"

	return 0


class GetOp(StorageOperation):

    def __call__(self, storages, name, element_name):

	if  storages.has_key(name):
	    storage = storages[name][0]
	    if element_name in storage.list():
		return Container(storage.get(element_name))
	else:
	    raise "No such storage %s " % name


class PopOp(StorageOperation):

    def __call__(self, storages, name, element_name):

	if  storages.has_key(name):
	    storage = storages[name][0]
	    if element_name in storage.list():
		return Container(storage.pop(element_name))
	else:
	    raise "No such storage %s " % name


	



class StorageCollectorDelegate(object):

    operations = {
	"add": AddOp(),
	"list":ListOp(),
	"get" :GetOp(), 
	"pop":PopOp()
	}


    def __init__(self, filename = "Oliva.db"):
	super(StorageCollectorDelegate, self).__init__()	
	self.main = StorageObject(filename)
	storages = self.main.get("storages")
	if not storages:
	    storages = {}
	    self.main.add("storages", storages)

    
    def opStorage(self, op, storage, *args):
	main = self.main.get("storages")
	return self.operations[op](main, storage, *args)
	
	    
    def newStorage(self, name, desc):
	storages = self.main.get("storages")
	if name in storages.keys():
	    raise "storage already exists"
	filename = name + "XXX.db"

	obj = StorageObject(filename)
	info = (obj, desc)
	try:
	    storages[name] = info 
	    self.main.update("storages", storages)
	except:
	    raise "Storage not created"
	
	return 1 
    


    def storages(self):
	return self.main.get("storages").keys()





class StorageCollector(object):

    def __init__(self, filename = "Oliva.db"):
	super(StorageCollector, self).__init__()	
	self.delegate = StorageCollectorDelegate(filename)

    def newStorage(self, *args):
	return self.delegate.newStorage(*args)

    def opStorage(self, *args):
	return self.delegate.opStorage(*args)

    def storages(self, *args):
	return self.delegate.storages(*args)
    
    











