# Twisted Imports
from twisted.words.protocols.jabber import client, jid, xmlstream
from twisted.words.xish.domish import Element
from twisted.internet.defer import Deferred

import string
from random import choice

from qi.xmpp.client.roster import RosterManager
from qi.xmpp.client.disco import ServerDiscovery
from qi.xmpp.client.vCard import vCard
import qi.xmpp.client.xmppComm as xmppComm
import qi.xmpp.client.ns as ns
from qi.xmpp.client.filetransfer import FileTransfer
from qi.xmpp.client.pingpong import PingPong

chars = string.letters + string.digits

class JabberClient:
	"""
	"""

	def __init__(self,myJID):
		"""
		"""
		me = myJID + "/support"
		self.vCard = vCard(self)
		self.avatar = None
		self.nickname = ''
		self.jabberID = jid.JID(me)
		self.jserver = myJID[myJID.find('@')+1:]
		self.xmlstream = None
		self.roster = RosterManager(self)
		self.disco = ServerDiscovery(self)
		self.filetransfer = FileTransfer(self)
		self.pingpong = PingPong(self)
		self.preMsgId = ''.join([choice(chars) for i in range(4)])
		
		self.messageID = 0
		self.deferredIqs = {}
		
	def login(self,password):
		"""
		"""
		self.jfactory = client.XMPPClientFactory(self.jabberID,password)
		self.jfactory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.authSuccess)
		self.jfactory.addBootstrap(client.IQAuthInitializer.INVALID_USER_EVENT,self.authfailedEvent)
		self.jfactory.addBootstrap(client.IQAuthInitializer.AUTH_FAILED_EVENT,self.authfailedEvent)
		self.jfactory.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.authfailedEvent)
		self.jfactory.addBootstrap(xmlstream.STREAM_END_EVENT,self.connectionLost)
		self.logginResult = Deferred()
		return self.logginResult
		
	def makeMessageID(self):
		self.messageID += 1
		return self.preMsgId+str(self.messageID)
	
	def connectionLost(self,reason):
		self.jfactory.stopTrying()		
	
	def authSuccess(self,xmlstream):
		self.logginResult.callback(True)
		del self.logginResult
		self.xmlstream = xmlstream
		#self.xmlstream.connectionLost = self.connectionLost
		
		self.xmlstream.addObserver(ns.PRESENCE,self.onPresence)
		self.xmlstream.addObserver(ns.MESSAGE,self.onMessage)
		self.xmlstream.addObserver(ns.IQ,self.onIq)
		#self.xmlstream.addObserver(ns.ANYTHING,self.onAnything)		
		self.roster.sendInitRosterRequest()

		self.afterLogin()
		
	def authfailedEvent(self,xmlstream):
		"""
		"""
		self.logginResult.callback(False)
		del self.logginResult
	
	def onMessage(self, el):
		""" Handles incoming message packets """
		fro = el.getAttribute("from")
		#froj = jid.JID(fro)
		
		mID = el.getAttribute("id")
		mtype = el.getAttribute("type")
		body = ""
		messageEvent = False
		noerror = False
		composing = None
		for child in el.elements():
			if(child.name == "body"):
				body = child.__str__()
			elif(child.name == "noerror" and child.uri == "sapo:noerror"):
				noerror = True
			elif(child.name == "x"):
				if(child.uri == ns.NS_XEVENT):
					messageEvent = True
					composing = False
					for child2 in child.elements():
						if(child2.name == "composing"):
							composing = True
							break

		# Check message event stuff
		if(body and messageEvent):
			self.typingUser = True
		elif(body and not messageEvent):
			self.typingUser = False
		elif(not body and messageEvent):
			self.typingNotificationReceived(fro, composing)


		if(body):
			# Save the message ID for later
			self.messageReceived(fro, mtype, body, noerror)

	
	def onIq(self, el):
		""" Decides what to do with an IQ """

		fro = el.getAttribute("from")
		ID = el.getAttribute("id")
		iqType = el.getAttribute("type")

		# Check if it's a response to a send IQ
		if self.deferredIqs.has_key(ID) and (iqType == "error" or iqType == "result"):
			self.deferredIqs[ID].callback(el)
			del self.deferredIqs[ID]
			return

		for query in el.elements():
			uri = query.uri
			for feature,handler in self.disco.features:
				if uri == feature:
					handler(el)
					return
		if fro:
			xmppComm.sendIqError(self.xmlstream,to=fro,fro=self.jabberID.full(), ID=ID, etype="cancel", condition="service-unavailable")


	def onPresence(self, el):
		""" Handles incoming presence packets """
		
		fro = el.getAttribute("from")
		froj = jid.JID(fro)
		to = el.getAttribute("to")
		toj = jid.JID(to)
		# Grab the contents of the <presence/> packet
		ptype = el.getAttribute("type")
		if ptype and (ptype.startswith("subscribe") or ptype.startswith("unsubscribe")):
			self.subscriptionReceived(fro, toj.userhost(), ptype)
		else:
			status = None
			show = None
			priority = None
			avatarHash = ""
			nickname = ""
			for child in el.elements():
				if(child.name == "status"):
					status = child.__str__()
				elif(child.name == "show"):
					show = child.__str__()
				elif(child.name == "priority"):
					priority = child.__str__()
				elif(child.uri == ns.NS_XVCARDUPDATE):
					avatarHash = " "
					for child2 in child.elements():
						if(child2.name == "photo"):
							avatarHash = child2.__str__()
						elif(child2.name == "nickname"):
							nickname = child2.__str__()

			if not ptype:
				# available presence
				if(avatarHash):
					self.avatarHashReceived(froj.userhost(), avatarHash)
				if(nickname):
					self.nicknameReceived(froj.userhost(), nickname)

			self.presenceReceived(froj.full(), priority, ptype, show, status)


	def sendMessage(self, to, body, mtype=None, delay=None):
		fro = self.jabberID.full()
		xmppComm.sendMessage(self,to,fro,body,mtype=mtype,delay=delay)

	def sendPresence(self, fro=None, to=None, show=None, status=None, priority=None, ptype=None, avatarHash=None, nickname=None, payload=[]):
		xmppComm.sendPresence(self, fro, to, show, status, priority, ptype, avatarHash, nickname, payload)

	def sendIq(self,el):
		return xmppComm.sendIq(self,el)
		
	def logout(self):
		self.sendPresence(fro=self.jabberID.full(),ptype="unavailable")
		
	def messageReceived(self, source, mtype, body, noerror):
		""" Override this method to be notified when a message is received """
		pass

	def inviteReceived(self, source, resource, dest, destr, roomjid):
		""" Override this method to be notified when an invitation is received """
		pass

	def presenceReceived(self, source, priority, ptype, show, status):
		""" Override this method to be notified when presence is received """
		pass

	def subscriptionReceived(self, source, dest, subtype):
		""" Override this method to be notified when a subscription packet is received """
		pass

	def nicknameReceived(self, source, nickname):
		""" Override this method to be notified when a nickname has been received """
		pass

	def avatarHashReceived(self, source, avatarHash):
		""" Override this method to be notified when an avatar hash is received """
		pass

	def typingNotificationReceived(self, source, composing):
		""" Override this method to be notified of a typing notification"""
		pass
		
	def rosterChanged(self,roster):
		""" Override this method to be notified of a roster change """

	def afterLogin(self):
		"""Override this method to perform actions after login"""
	
	def acceptFile(self,fromj,name,descr,size):
		"""Override this method to specify whether a file transfer should be accepted"""
		return True
		
	def fileReceived(self,fromj,name,value):
		"""
		"""
		