from salamoia.h2o.feedcollection import FeedCollection
from salamoia.h2o.logioni import Ione
#from salamoia.h2o.exception import *
from salamoia.h2o.container import Container

class FeedControl(object):
    def __init__(self):
	self.feeds = FeedCollection("/tmp/news.db")
	Ione.log("FeedControl init")
        super(FeedControl, self).__init__()


	
    def getNewsCollection(self, user):
	Ione.log("NewsCollection request for user " + user)
	"""
	To recive the news feed object about 
	one user or general information
	"""
	return Container(self.feeds.getFeed(user))


    def getNewsList(self, user):
	Ione.log("List of news request for " + user)
	"""
	get list of news for the user 
    	"""
	feed = self.feeds.getFeed(user)
	
	return feed.list()



    def getNews(self, user, title):
	Ione.log("NewsCollection request for user " + user)
	"""
	To recive one specific news
	"""
	feed = self.feeds.getFeed(user)
	return feed[title]

"""
TODO: controllo errore e immissione 
"""

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
