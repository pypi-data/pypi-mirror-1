from object import Object
import shelve 
import string 


"""
this class implement generic information flow 
to an specific user or to any user
"""

class GenericCollection(object):

    def __init__(self, filename="news.db"):
	self.myNews = []
	self.filename = filename

    def getList(self):
	try:
	    data = shelve.open(self.filename)
	except:
	    raise
	keys = data.keys()
	data.close() 
	return keys

    def addKey(self, key):
	try:
	    data = shelve.open(self.filename)
	except:
	    raise
	data[key] = []
	data.close()

    def pushThing(self, key, thing):
	try:
	    data = shelve.open(self.filename)
	except:
	    raise
	if data.has_key(key):
	    data[key] = thing
	    data.close()	
	else: 
	    data[key] = thing
	    data.close()
	    
    def popThing(self,key):
	data = shelve.open(self.filename)
	if data.has_key(key):
	    ret = data[key]
	    data.close()
        else:
	    return None
	
class FeedCollection(GenericCollection):
    
    def __init__(self, filename = "feed.db"):
	#GenericCollection.__init__(self, filename )
        super(FeedCollection, self).__init__(filename)
	
    def getUsers(self): 
	return super(FeedCollection, self).getList()
    	
    def getFeed(self,user):
	feed = super(FeedCollection, self).popThing(user)
	if feed:
	    return feed 
	else:
	    return None
	   
    def addFeed(self, user, thing):
	return super(FeedCollection, self).pushThing(user, thing)


class NewsCollection(Object):
    def __init__(self):
	self.news = {}
	self.items = {}

    def list(self):
	for  i in self.news.keys():
	    self.items[i] = self.news[i].attributes['url']
	return self.items
    
    def collect(self, title, info):
	self.news[title] = info
	
    def decollect(self, title):
	return self.news.pop(title)
    

class News:
    def __init__(self):
	self.attributes = {}
	self.attributes["title"] = "New about ..."
	self.attributes["date"] = "19-12-2004"
	self.attributes["url"] = "/user/news"
	self.attributes["body"] = "nuova news bla bla"
	self.attributes["description"] = "nuova news bla bla"

    def listAttr(self):
	return self.attributes.keys()

    def addAttr(self, name, value):
	self.attributes[name] = value
	
    def delAttr(self, name):
	return self.attributes.pop(name)


