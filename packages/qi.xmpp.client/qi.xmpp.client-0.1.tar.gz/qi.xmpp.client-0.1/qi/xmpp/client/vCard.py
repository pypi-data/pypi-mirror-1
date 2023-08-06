from twisted.words.xish.domish import Element

import qi.xmpp.client.ns as ns

class vCard:
	"""
	"""
	def __init__(self,client):
		self.client = client
		
	def getOwnVCard(self):
		iq = Element(("","iq"))
		iq["from"] = self.client.jabberID.full()
		iq["type"] ="get"
		iq["id"] = self.client.makeMessageID()
		iq.addElement((ns.NS_VCARDTEMP,"vCard"))
		return self.client.sendIq(iq)
		
	def setOwnVCard(self,FN="",DESC=""):
		"""
		"""
		iq = Element(("jabber:client","iq"))
		iq["from"] = self.client.jabberID.full()
		iq["type"] ="set"
		iq["id"] = self.client.makeMessageID()
		vCard = iq.addElement((ns.NS_VCARDTEMP,"vCard"))

		if FN:
			vCard.addElement("FN",content=FN)
		if DESC:
			vCard.addElement("DESC",content=DESC)
		if self.client.avatar:
			vCard.addChild(self.client.avatar.makePhotoElement())
		return self.client.sendIq(iq)

	def getUserVCard(self,to):
		iq = Element(("jabber:client","iq"))
		iq["from"] = self.client.jabberID.full()
		iq["to"] = to
		iq["type"] ="get"
		iq["id"] = self.client.makeMessageID()
		iq.addElement((ns.NS_VCARDTEMP,"vCard"))
		return self.client.sendIq(iq)