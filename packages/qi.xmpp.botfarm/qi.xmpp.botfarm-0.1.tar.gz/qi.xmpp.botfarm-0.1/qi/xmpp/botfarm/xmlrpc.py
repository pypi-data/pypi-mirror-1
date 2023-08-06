from twisted.web import server
from twisted.internet import defer
from twisted.web.xmlrpc import XMLRPC
from qi.xmpp.botfarm.logutil import LogEvent, INFO, WARN, ERROR
import qi.xmpp.botfarm.config as config
import xmlrpclib 
Fault = xmlrpclib.Fault
class XMLRPCServer(XMLRPC):
	"""
	""" 
	def __init__(self,sm):
		XMLRPC.__init__(self)
		self.sm = sm
		self.adminSession = self.sm.sessions["@".join([config.admin_id,config.server])]
	

	def render(self, request):
		""" We override render just to make sure addUser and delUser requests come from authorized IP's...
		"""
		request.content.seek(0, 0)
		request.setHeader("content-type", "text/xml")
		try:
			args, functionPath = xmlrpclib.loads(request.content.read())
		except Exception, e:
			f = Fault(self.FAILURE, "Can't deserialize input: %s" % (e,))
			self._cbRender(f, request)
		else:
			try:	
				if functionPath in ['addUser','delUser','getNoRegisteredUsers']:
					clientIP = request.getClientIP() 
					if clientIP not in config.xmlrpc_admin_accept_ips:
						LogEvent(ERROR,"Unauthorized request from %s"%clientIP)
						raise Fault(self.FAILURE, "Unauthorized request")
				function = self._getFunction(functionPath)
			except Fault, f:
				self._cbRender(f, request)
			else:
				defer.maybeDeferred(function, *args).addErrback(
					self._ebRender
				).addCallback(
					self._cbRender, request
				)
		return server.NOT_DONE_YET



	#Admin interface

	def xmlrpc_addUser(self,username,userpass):
		userjid = self.adminSession.addUser(username,userpass)
		LogEvent(INFO,userjid)
		if userjid:
			return userjid
		else:
			return False

	def xmlrpc_delUser(self,username):
		result = self.adminSession.delUser(username)
		return result

	def xmlrpc_getNoRegisteredUsers(self):
		return self.adminSession.getNoRegisteredUsers()


	# Session Manager

	def xmlrpc_loadBot(self,botjid,password,persistent=False):
		return self.sm.loadBot(botjid,password,persistent)
		
	def xmlrpc_unloadBot(self,botjid):
		self.sm.delSession(botjid)
		return True
	
	# Bot interface
	
	def xmlrpc_userLogin(self,botjid,userID,name,subject):
		"""
		"""
		if not self.sm.sessions.has_key(botjid):
			return (False,'')
		bot = self.sm.sessions[botjid]
		return bot.userLogin(userID,name,subject)
	
	def xmlrpc_userLogout(self,botjid,userID):
		"""
		"""
		if not self.sm.sessions.has_key(botjid):
			return False
		bot = self.sm.sessions[botjid]
		return bot.userLogout(userID)
	
	def xmlrpc_getUserMessages(self,botjid,userID):
		"""
		"""
		if not self.sm.sessions.has_key(botjid):
			return (False,[])
		bot = self.sm.sessions[botjid]
		return bot.getUserMessages(userID)
		
	def xmlrpc_sendUserMessage(self,botjid,userID,body):
		"""
		"""
		if not self.sm.sessions.has_key(botjid):
			return False
		bot = self.sm.sessions[botjid]
		return bot.sendUserMessage(userID,body)
	
	def xmlrpc_getContactAvatarB64(self,botjid,userID):
		if not self.sm.sessions.has_key(botjid):
			LogEvent(INFO,"BOT %s NOT FOUND"%botjid)
			return ''
		
		bot = self.sm.sessions[botjid]
		return bot.getContactAvatarB64(userID)
	
	def xmlrpc_addContact(self,botjid,contactjid,group=None):
		if not self.sm.sessions.has_key(botjid):
			return False
		return self.sm.sessions[botjid].roster.addContact(contactjid,group)

	def xmlrpc_delContact(self,botjid,contactjid):
		if not self.sm.sessions.has_key(botjid):
			return False
		return self.sm.sessions[botjid].roster.removeContact(contactjid)
	
	def xmlrpc_getContacts(self,botjid):
		if not self.sm.sessions.has_key(botjid):
			return []
		return list(self.sm.sessions[botjid].roster.getContacts())
	
	def xmlrpc_getAliveContacts(self,botjid):
		if not self.sm.sessions.has_key(botjid):
			return []
		return list(self.sm.sessions[botjid].aliveAgents)

	def xmlrpc_getAvailableContacts(self,botjid):
		if not self.sm.sessions.has_key(botjid):
			return []
		return list(self.sm.sessions[botjid].availableAgents())

	def xmlrpc_getContactVCard(self,botjid,userID):
		if not self.sm.sessions.has_key(botjid):
			return {}
		return self.sm.sessions[botjid].getContactVCard(userID)
		
		
		