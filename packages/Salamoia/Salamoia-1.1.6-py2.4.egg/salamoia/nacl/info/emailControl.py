from salamoia.h2o.object import Object
from email.Message import Message 
from email.Parser import * 
from salamoia.h2o.template import * 
from salamoia.h2o.logioni import *
from salamoia.h2o.exception import *
from salamoia.h2o.container  import *
from smtplib import *
from salamoia.nacl.info.sendmail import sendmail
from salamoia.nacl.backend import *
import os


"""
Mail control manages only email.Message objects

"""

class MailControl(object):
    def __init__(self, filename = "Mail.db"):
	super(MailControl, self).__init__()
	varPath = NACLBackend.defaultBackend().varPath()
	self.engine = TemplateEngine(varPath, filename )


    def getMail(self, user, key):
	mails = self.engine.get(user)
	return Container(mails[key])


    def addMail(self, user, mail, mailKey="Subject"):
	key = mail[mailKey]

	try:
	    mails = self.engine.get(user)
	    mails[key] = mail
	    self.engine.add(user, mails)

	except:
	    mails = {}
	    mails[key] = mail
	    self.engine.add(user, mails)

	return 1

    def delMail(self, user, key):
        Ione.log("deleting mail for", user, key)
        mails = self.engine.get(user)
        del mails[key]
        self.engine.add(user, mails)
        return 1
    
    def listMail(self, user):
	try:
	    mails = self.engine.get(user).keys()
	except:
	    mails = []
	    
	return Container(mails)


    def send(self, mail):
        return sendmail(mail)


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
