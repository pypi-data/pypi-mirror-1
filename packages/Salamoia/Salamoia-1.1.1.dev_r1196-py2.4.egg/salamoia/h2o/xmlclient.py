#!/usr/bin/python -O
#
# baseClient.py
#	Description:	A basic client for baseserver.  Unless you need to do
#			something special, you should not need to write your
#			own client for your server.  This client automagically
#			knows what commands the server offers and lets the user
#			call them.  It is currently limited to four args for
#			the server functions, so if you need more, either
#			make a class that inherits this one and make a member
#			function there (easy), or hack Client to allow more
#			args.  BTW - this was not my choice... python's scoping
#			sucks with lambdas.
#
#	Requires: 	xmlrpc
#
#
#	Copyright:	LGPL
#	Created:	March 20, 2001
#	Author:		Chris Jensen - chris@sourcelight.com
#
#	Last Update:	04/25/2001
#
#####################################################################################

import xmlrpc
from salamoia.h2o.logioni import *
import traceback 

LOG_LEVEL	= 0
ClientError	= 'ClientError'
ERR_CLOSE	= 'Connection is closed.  Call reconnect.'
NONE		= []

# Client
#
# Client(host, port, timeout)
#	Constructor.  host and port are the server to connect to.  timeout is the
#	maximum time you should wait for the server to procedd your request.  A
#	value less than 0 means block until the server responds.
#
# reconnect()
#	Reconnect to the server if the connection is lost.
#
# The rest of the callable functions are provided by the server.  To get a command
# list, call the usage function, which SHOULD return a complete list of functions
# and thier usage.  Obviously, if you write the server, you know what's there.
#
class Client:
	def __init__(self, host, port, timeout=-1.0, username=None, password=None):
		self.host	= host			# host
		self.port	= port			# server port
		self.timeout	= timeout		# xmlrpc timeout
		self.client	= xmlrpc.client(host, port)
		self.username   = username
		self.password   = password
		xmlrpc.setLogLevel(LOG_LEVEL)
		self.cmds	= self.__talk__('getclient')
		if not self.cmds:
			raise ClientError, 'could not get command list'

	def __getattr__(self, fn):
		if fn not in self.__dict__['cmds']:
			raise AttributeError, '%s instance has no attribute %s' % (
						self.__class__, fn)
		return (lambda a1=NONE,a2=NONE,a3=NONE,a4=NONE,x=fn,y=self.__talk__:
		       y(x, a1, a2, a3, a4))

###
## special commands.
##
	# kill the server
	#
	def kill(self):
		if not self.client:
			raise ClientError, ERR_CLOSE
		self.timeout	= 1.0
		try:	self.__talk__('kill')
		except:	pass
		self.client	= None

	# disconnect from the server
	#
	def leave(self):
		self.__talk__('leave')
		self.client	= None

	# reconnect to the server
	#
	def reconnect(self):
		self.client	= xmlrpc.client(self.host, self.port)

###
## helper functions
##
	# do a send and receive with the server
	#
	def __talk__(self, command, *args):		
		args	= filter(lambda x,y=NONE: (x is not y), args)
		args    = map(self.__mapobjects__, args)
		if not self.client:
			raise ClientError, ERR_CLOSE
		try:
			res =  self.client.execute(command, args,
						   self.timeout,
						   self.username,
						   self.password)			
			if Object.isPickled(res):
				return Object.decapsulePickled(res, dir=Object.SERVER_TO_CLIENT)
			return res
		except:
#		        traceback.print_exc()
                        if not isinstance(sys.exc_value, str) and not isinstance(sys.exc_value, tuple):
			  Ione.log("DIOCANE piglato un exception di", sys.exc_value.faultString)
                        else:
                          Ione.log("DIOCANE piglato un exception di stinghia:", sys.exc_value)
			raise
			#self.client = xmlrpc.client(self.host, self.port)
			#return self.client.execute(command, args,
			#			   timeout=self.timeout)
	def __mapobjects__(self, x):
		if isinstance(x, Object):
			return Object.pickledEncapsulation(x, dir=Object.CLIENT_TO_SERVER)
		else:
			return x

from salamoia.h2o.object import Object
