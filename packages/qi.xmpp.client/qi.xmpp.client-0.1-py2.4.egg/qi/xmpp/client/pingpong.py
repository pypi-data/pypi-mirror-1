from twisted.words.xish.domish import Element
from twisted.words.protocols.jabber.client import IQ
import qi.xmpp.client.xmppComm as xmppComm

class PingPong(object):
	"""
	XEP 0199: xmpp ping
	http://www.xmpp.org/extensions/xep-0199.html
	Does NOT support pinging, only ponging.
	"""	
	
	def __init__(self,client):
		self.client = client
		
	def onPing(self,el):
		fr = el["from"]
		pid = el["id"]
		pong = Element(("jabber:client", "iq"))
		pong["from"] = self.client.jabberID.full()
		pong["to"] = fr
		pong["id"] = pid
		pong["type"] = result
		xmppComm.sendIq(self.client,pong)
		print "KAKAKAKAKAKA"
