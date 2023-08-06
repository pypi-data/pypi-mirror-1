from twisted.words.xish.domish import Element
import qi.xmpp.client.ns as ns

class ServerDiscovery:
	"""
	"""
	def __init__ (self, client):
		
		self.client = client
		self.identities = set()
		self.features = set()

	def addIdentity(self, category, ctype, name):
		""" Adds an identity to the discovery profile. """
		self.identities.add((category, ctype, name))

	def addFeature(self, var, handler):
		""" Adds a feature to the discovery profile. """
		self.features.add((var, handler))

	def onDiscoInfo(self,el):
		""" Send a service discovery disco#info stanza to the sender.
		"""
		iqType = el.getAttribute("type")
		if iqType == "get":
			to = el.getAttribute("from")
			ID = el.getAttribute("id")
		
			iq = Element((None, "iq"))
			iq.attributes["type"] = "result"
			iq.attributes["from"] = self.client.jabberID.full()
			iq.attributes["to"] = to
			if(ID):
				iq.attributes["id"] = ID
			query = iq.addElement((ns.NS_DISCO_INFO,"query"))

			# Add any identities
			for (category, ctype, name) in self.identities:
				identity = query.addElement("identity")
				identity.attributes["category"] = category
				identity.attributes["type"] = ctype
				identity.attributes["name"] = name

			# Add any supported features
			for (var, handler) in self.features:
				feature = query.addElement("feature")
				feature.attributes["var"] = var
			self.client.xmlstream.send(iq)
	
	def onApplicationVersion(self,el):
		to = el.getAttribute("from")
		ID = el.getAttribute("id")
		
		iq = Element((None, "iq"))
		iq.attributes["type"] = "result"
		iq.attributes["from"] = self.client.jabberID.full()
		iq.attributes["to"] = to
		if(ID):
			iq.attributes["id"] = ID
		query = iq.addElement((ns.NS_IQVERSION,"query"))
		name = query.addElement("name")
		name.content="qi.xmpp.client"
		version = query.addElement("version")
		version.content="0.1"
		self.client.xmlstream.send(iq)
	
	def sendDiscoInfoRequest(self,to):
		iq = Element((ns.NS_CLIENT,"iq"))
		iq["from"] = self.client.jabberID.full()
		iq["to"] = to
		iq["type"] = "get"
		iq["id"] = self.client.makeMessageID()
		iq.addElement((ns.NS_DISCO_INFO,"query"))
		d = self.client.sendIq(iq)
		return d
		
