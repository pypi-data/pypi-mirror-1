from twisted.internet import reactor
from twisted.words.protocols.jabber import jid
from twisted.words.xish.domish import Element
from twisted.words.xish import xpath
import base64

from qi.xmpp.client.client import JabberClient
from qi.xmpp.botfarm.logutil import LogEvent, INFO, WARN, ERROR
from qi.xmpp.client.avatar import parsePhotoEl
import qi.xmpp.botfarm.config as config
class Session(JabberClient):
	"""
	"""
	
	def __init__(self,jid,sessionManager,avatar=None,persistent=False):
		"""
		"""
		JabberClient.__init__(self,jid)		
		self.sm = sessionManager
		self.avatar = avatar
		self.nickname = 'support bot'
		self.aliveAgents = set()
		self.aliveUsers = set()
		self.userMessages = dict()
		self.userFiles = dict()
		self.userLinks = dict()
		self.agentAvatars = dict()
		self.agentVCards = dict()
		self.filesToReceive = dict()
		self.persistent = persistent
	
	def availableAgents(self):
		return self.aliveAgents - set(self.userLinks.keys())
	def userLogin(self,userID,name,subject):
		available = self.availableAgents()
		if available:
			available = available.pop()
			self.userLinks[available] = userID
			self.userMessages[userID] = []
			self.userFiles[userID] = []
			self.aliveUsers.add(userID)
			self.sendMessage(available,body = "User %s joined support. Subject: %s"%(name,subject))
			LogEvent(INFO,self.jabberID.full(),"User %s joined support. Agent: %s Subject: %s"%(name,available,subject))
			return (True,available)
		LogEvent(INFO,self.jabberID.full(),"User %s could not join support. No available users"%name)		
		return (False,'')
		
	def userLogout(self,userID):
		"""
		"""
		for agent in self.userLinks.keys():
			if self.userLinks[agent]==userID:
				self.sendMessage(agent,"User left.")
				del self.userLinks[agent]
				del self.userMessages[userID]
				del self.userFiles[userID]
				if userID in self.aliveUsers:
					self.aliveUsers.remove(userID)
		return (True)
		
	def getUserMessages(self,userID):
		if self.userMessages.has_key(userID):
			messages = self.userMessages[userID]
			files = self.userFiles[userID]
			self.userMessages[userID] = []
			self.userFiles[userID] = []
			self.aliveUsers.add(userID)
			return (True,messages,files)
		return (False,[],[])
	
	def sendUserMessage(self,userID,body):
		"""
		"""
		for agent in self.userLinks.keys():
			if self.userLinks[agent]==userID:
				self.sendMessage(agent,body=body)
				return True
		return False
	
	def getContactAvatarB64(self,userID):
		"""
		"""
		for agent in self.userLinks.keys():
			if self.userLinks[agent]==userID:
				agent = jid.JID(agent).userhost()
				break
		try:
			aHash = self.agentAvatars[agent]
			avatar = self.sm.avatarStorage.getAvatarData(aHash)
			avatar = base64.encodestring(avatar)
			return avatar
		except:
			return ''
	def getContactVCard(self,userID):
		"""
		"""
		for agent in self.userLinks.keys():
			if self.userLinks[agent]==userID:
				agent = jid.JID(agent).userhost()
				break
		try:
			vCard = self.agentVCards[agent]
			return vCard
		except:
			return {'FN':'','DESC':''}
		
		
	def afterLogin(self):
		"""
		"""
		avatarHash = ""
		if self.avatar:
			avatarHash = self.avatar.getImageHash()
		#Send initial empty presence to server
		self.sendPresence(fro=self.jabberID.full(), show='chat', status='Online', avatarHash=avatarHash, nickname=self.nickname,priority="1")
		
		reactor.callLater(config.connection_timeout,self.cleanup)
		LogEvent(INFO,self.jabberID.full(),"Logged in.")

	def cleanup(self):
		for user in self.userLinks.values():
			if user not in self.aliveUsers:
				self.userLogout(user)
		if not self.aliveUsers and not self.persistent:
			LogEvent(INFO,self.jabberID.full(),"Self destroying in cleanup.")
			self.sm.delSession(self.jabberID.userhost())
			return	
		
		self.aliveUsers = set()
		reactor.callLater(config.connection_timeout, self.cleanup)
		LogEvent(INFO,self.jabberID.full(),"Cleanup")
		
	def subscriptionReceived(self, source, dest, subtype):
		"""
		"""
		
		sourceuh = jid.JID(source).userhost()
		if subtype == "subscribe":
			if sourceuh in self.roster.roster:
				self.sendPresence(to=source, ptype="subscribed")
				LogEvent(INFO,self.jabberID.full(),"%s subscribed to me"%source)
			else:
				self.sendPresence(to=source, ptype="unsubscribed")
				LogEvent(INFO,self.jabberID.full(),"refused subscription to %s"%source)
		elif subtype == "subscribed":
			self.sendPresence(to=source, ptype="subscribed")
			LogEvent(INFO,self.jabberID.full(),"I subscribed to %s"%source)
			
			
		elif subtype == "unsubscribe":
			self.sendPresence(to=source, ptype="unsubscribed")
		elif subtype == "unsubscribed":
			self.sendPresence(to=source, ptype="unsubscribed")
		else:
			LogEvent(WARN,self.jabberID.full(),"Ignored subscription: %s"%subtype)

	def presenceReceived(self, source, priority, ptype, show, status):
		"""
		"""
		if ptype == "probe":
			LogEvent(INFO, self.jabberID.full(), "Responding to presence probe")
			avatarHash = ""
			if self.avatar:
				avatarHash = self.avatar.getImageHash()
			self.sendPresence(to=source, fro=self.jabberID.full(), show='chat', status='Online', avatarHash=avatarHash, nickname=self.nickname)
		elif ptype == "unavailable":
			LogEvent(INFO,self.jabberID.full(),"%s logged out"%source)
			self.contactUnavailable(source,show,status,priority)

		else:
			LogEvent(INFO,self.jabberID.full(),"%s updated presence, show:%s status:%s priority:%s"%(source,show,status,priority))
			if show in ["xa","away","dnd"]:
				self.contactUnavailable(source,show,status,priority)
			elif source!=self.jabberID.full():
				self.contactAvailable(source,show,status,priority)
				
	def messageReceived(self, source, mtype, body, noerror):
		"""
		"""
		LogEvent(INFO,self.jabberID.full(),"Received MSG of type %s from %s:%s"%(mtype,source,body))
		if self.userLinks.has_key(source):
			receiver = self.userLinks[source]
			self.userMessages[receiver].append(body)
		
	def typingNotificationReceived(self, source, composing):
		"""
		"""
		LogEvent(INFO,self.jabberID.full(),"Received typing notif.from %s:%s"%(source,composing))
	
	def nicknameReceived(self, source, nickname):
		"""
		"""
		LogEvent(INFO,self.jabberID.full(),"Nickname received from %s:%s"%(source,nickname))

	def avatarHashReceived(self, source, avatarHash):
		"""
		"""
		self.agentAvatars[source]= avatarHash
		if not self.sm.avatarStorage.hasAvatar(avatarHash):
			d = self.vCard.getUserVCard(source)
			d.addCallback(self.vCardReceived)
			LogEvent(INFO,self.jabberID.full(),"Avatar hash received from %s:%s"%(source,avatarHash))
			
	def vCardReceived(self,iq):
		"""
		"""
		fromj = iq["from"]
		
		photo = xpath.queryForNodes('/iq/vCard/PHOTO',iq)
		if photo:
			imgData = parsePhotoEl(photo[0])
			key = self.sm.avatarStorage.setAvatar(imgData)
		FN = xpath.queryForString('/iq/vCard/FN',iq)
		DESC = xpath.queryForString('/iq/vCard/DESC',iq)
		self.agentVCards[fromj] = {'FN':FN,'DESC':DESC}
		LogEvent(INFO,self.jabberID.full(),"vCard received from %s"%fromj)		
		
	def contactAvailable(self,contact,show,status,priority):
		"""
		"""		
		self.aliveAgents.add(contact)
		LogEvent(INFO,self.jabberID.full(),"%s available:show:%s status:%s priority:%s"%(contact,show,status,priority))
		
	def contactUnavailable(self,contact,show,status,priority):
		if contact in self.aliveAgents:
			self.aliveAgents.remove(contact)
		LogEvent(INFO,self.jabberID.full(),"%s unavailable:show:%s status:%s priority:%s"%(contact,show,status,priority))
		
	def acceptFileTransfer(self,fromj,name,descr,size):
		if int(size) < config.filesize_limit:
			self.filesToReceive[(fromj,name)] = descr
			LogEvent(INFO,self.jabberID.full(),"Accepted file transfer from %s.File:%s %s Size:%s"%(fromj,name,descr,size))
			return True
		LogEvent(INFO,self.jabberID.full(),"Rejected file transfer: %s %s %s"%(name,descr,size))
		return False
		
	def fileReceived(self,fromj,name,value):
		"""
		"""
		filepath = "/tmp/"+name
		file = open(filepath,"w")
		file.write(value)
		file.close()
		try:
			userid = self.userLinks[fromj]
			descr = self.filesToReceive[(fromj,name)]
			del self.filesToReceive[(fromj,name)]
			self.userFiles[userid].append([filepath,name,descr])
		except Exception,Detail:
			LogEvent(WARN,self.jabberID.full(),"Exception in fileReceived:%s"%Detail)
	
	def rosterChanged(self,roster):
		"""
		"""
		LogEvent(INFO,"ROSTER UPDATE")