from twisted.words.xish.domish import Element
from twisted.words.xish import xpath
import qi.xmpp.client.ns as ns
import qi.xmpp.client.xmppComm as xmppComm
class RosterManager(object):
	"""
	"""
	def __init__(self,client):
		self.roster = set()
		self.client = client

	def onRosterUpdate(self,el):
		"""
		"""
		contacts = xpath.queryForNodes('//item',el) or []
		
		for node in contacts:
			jid = node["jid"]
			if node["subscription"] in ["to","both"] or node["subscription"]=="none" and node.getAttribute("ask")=="subscribe":
				self.roster.add(jid)

			elif node["subscription"] == "remove" and jid in self.roster:
				self.roster.remove(jid)
		
		if el["type"]=="set":
			result = Element(("","iq"))
			result["id"] = el["id"]
			result["type"]="result"
			xmppComm.sendIqResult(self.client,result)

	def sendInitRosterRequest(self):
		"""
		Send roster import
		"""
		
		iq = Element(("","iq"))
		iq["from"] = self.client.jabberID.full()
		iq["id"] = self.client.makeMessageID()
		iq["type"]="get"
		iq.addElement((ns.NS_IQROSTER,"query"))
		d = xmppComm.sendIq(self.client,iq)
		d.addCallback(self.onRosterUpdate)
	
	def addContact(self,contactJID,group=None):
		"""
		"""
		iq = Element(("","iq"))
		iq["id"] = self.client.makeMessageID() 
		iq["type"] = "set"
		query = iq.addElement((ns.NS_IQROSTER,"query"))
		item = query.addElement("item")
		item["jid"] = contactJID
		if group:
			item.addElement("group",content=group)
		xmppComm.sendIq(self.client,iq)
		#Send subscription presence
		self.client.sendPresence(to=contactJID, fro=self.client.jabberID.userhost(), ptype="subscribe")
		return True
		
	def removeContact(self,contactJID):
		"""
		"""
		iq = Element(("","iq"))
		iq["id"] = self.client.makeMessageID() 
		iq["type"] = "set"
		query = iq.addElement((ns.NS_IQROSTER,"query"))
		item = query.addElement("item")
		item["jid"] = contactJID
		item["subscription"] = "remove"
		xmppComm.sendIq(self.client,iq)
		self.client.sendPresence(to=contactJID, fro=self.client.jabberID.userhost(), ptype="unsubscribe")
		return True
	
	def getContacts(self):
		"""
		"""
		return self.roster
		