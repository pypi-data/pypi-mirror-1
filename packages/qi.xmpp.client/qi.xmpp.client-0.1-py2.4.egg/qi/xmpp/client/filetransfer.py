from twisted.words.xish.domish import Element
from twisted.internet import protocol, reactor, error
import sha
import StringIO
import struct

import qi.xmpp.client.ns as ns
import qi.xmpp.client.xmppComm as xmppComm

fileTransferSupportedFeatures = [ns.NS_S5B]


class FileTransfer:
	def __init__(self,client):
		self.client = client
		self.sessions = {}
		
	def onStreamInitiation(self,el):
		
		iqType = el["type"]
		fromj = el["from"]
		ID = el["id"]
		si = el.si
		if si:
			sid = si["id"]
			file = si.file
			filename = file["name"]
			filesize = file["size"]
			filedescr = file.desc
			if filedescr:
				filedescr = str(filedescr)
			else:
				filedescr = ''
			if not self.client.acceptFileTransfer(fromj,filename,filedescr,filesize):
				xmppComm.sendIqError(self.client.xmlstream, to=fromj,fro=self.client.jabberID.full(), ID=ID, etype="cancel", condition="forbidden")
				return
			try:
				field = si.feature.x.field
			except:
				xmppComm.sendIqError(self.client.xmlstream,to=fromj,fro=self.client.jabberID.full(), ID=ID, etype="cancel",condition="bad-request")
				return
				
			supportedFeatures = []
			for option in field.elements():
				supportedFeatures.append(str(option.value))

			preferredFeature = None
			for feature in fileTransferSupportedFeatures:
				if feature in supportedFeatures:
					preferredFeature = feature
					break
		
			if not preferredFeature:
				xmppComm.sendIqError(self.client.xmlstream,to=fromj,fro=self.client.jabberID.full(), ID=ID, etype="cancel",condition="bad-request")
				return
				
			def errOut():
				pass
				
			def startTransfer(consumer):
				new_iq = Element((ns.NS_CLIENT, 'iq'))
				new_iq['type'] = 'result'
				new_iq['id'] = ID
				new_iq['to'] = fromj

				# response with stream-method
				new_iq.addElement('si', ns.NS_SI)
				new_iq.si['id'] = sid
				new_iq.si.addElement('feature', ns.NS_FEATURE_NEG)
				new_iq.si.feature.addElement('x', ns.NS_XDATA)
				new_iq.si.feature.x['type'] = 'submit'
				new_iq.si.feature.x.addElement("field")['var'] = 'stream-method'
				new_iq.si.feature.x.field.addElement("value", content=preferredFeature)
				self.client.xmlstream.send(new_iq)
				self.sessions[(fromj, sid)] = consumer

			fs = FTSend(self.client, fromj, startTransfer, errOut, filename, filesize)
			rf = StringBuffer(fromj,filename,self.fileReceived)
			rf.error = lambda: None
			fs.accept(rf)
			
			
	def onInitSOCKS5(self,iq):
		"""
		"""
		sid = iq.query['sid']
		def get_streamhost(e):
			result = {}
			result['jid'] = e.getAttribute('jid')
			result['host'] = e.getAttribute('host')
			result['port'] = e.getAttribute('port')
			result['zeroconf'] = e.getAttribute('zeroconf')
			return result
			
		host_list = [get_streamhost(e) for e in iq.query.elements()]
		
		def validStreamHost(host):
			for streamhost in host_list:
				if streamhost['host'] == host:
					streamhost_jid = streamhost['jid']
					break
			else:
				return # couldn't find a jid for this host
			for connector in f.connectors:
				try:
					connector.stopConnecting()
				except error.NotConnectingError:
					pass
			if f.streamHostTimeout:
				f.streamHostTimeout.cancel()
				f.streamHostTimeout = None
			shiq = Element((ns.NS_CLIENT, "iq"))
			shiq['id'] = iq['id']
			shiq['to'] = iq['from']
			shiq['type'] = 'result'
			shiq.addElement("query", ns.NS_S5B)
			s = shiq.query.addElement("streamhost-used")
			s['jid'] = streamhost_jid
			self.client.xmlstream.send(shiq)
		
		consumer = self.sessions[(iq['from'], sid)]

		if not consumer:
			return

		f = protocol.ClientFactory()
		f.protocol = JEP65ConnectionSend
		f.consumer = consumer
		f.hash = sha.new(sid + iq['from'] + iq['to']).hexdigest()
		f.madeConnection = validStreamHost
		f.connectors = []
		f.streamHostTimeout = reactor.callLater(120, consumer.error)
		for streamhost in host_list:
			if streamhost['host'] and streamhost['port']:
				f.connectors.append(reactor.connectTCP(streamhost['host'], int(streamhost['port']), f))

	
	def fileReceived(self,fromj,filename,value):
		"""
		"""
		self.client.fileReceived(fromj,filename,value)

class StringBuffer(StringIO.StringIO):
	def __init__(self,fromj, filename,notifyFunc):
		self.notifyFunc = notifyFunc
		self.filename = filename
		self.fromj = fromj
		StringIO.StringIO.__init__(self)
	def close(self):
		self.notifyFunc(self.fromj,self.filename,self.getvalue())
		StringIO.StringIO.close(self)

class FTSend:
	def __init__(self, entity, to, startTransfer, cancelTransfer, filename, filesize):
		self.startTransfer = startTransfer
		self.cancelTransfer = cancelTransfer
		self.filename = filename
		self.filesize = filesize
		self.entity = entity
	def accept(self, filebuffer):
		self.startTransfer(filebuffer)
		self.cleanup()
	def reject(self):
		self.cancelTransfer()
		self.cleanup()
	def cleanup(self):
		del self.startTransfer, self.cancelTransfer


class JEP65ConnectionSend(protocol.Protocol):
	STATE_INITIAL = 1
	STATE_WAIT_AUTHOK = 2
	STATE_WAIT_CONNECTOK = 3
	STATE_READY = 4

	def __init__(self):
		self.state = self.STATE_INITIAL
		self.buf = ""

	def connectionMade(self):
		self.transport.write(struct.pack("!BBB", 5, 1, 0))
		self.state = self.STATE_WAIT_AUTHOK

	def connectionLost(self, reason):
		if self.state == self.STATE_READY:
			self.factory.consumer.close()
		else:
			self.factory.consumer.error()

	def _waitAuthOk(self):
		ver, method = struct.unpack("!BB", self.buf[:2])
		if ver != 5 or method != 0:
			self.transport.loseConnection()
			return
		self.buf = self.buf[2:] # chop

		# Send CONNECT request
		length = len(self.factory.hash)
		self.transport.write(struct.pack("!BBBBB", 5, 1, 0, 3, length))
		self.transport.write("".join([struct.pack("!B" , ord(x))[0] for x in self.factory.hash]))
		self.transport.write(struct.pack("!H", 0))
		self.state = self.STATE_WAIT_CONNECTOK

	def _waitConnectOk(self):
		ver, rep, rsv, atyp = struct.unpack("!BBBB", self.buf[:4])
		if not (ver == 5 and rep == 0):
			self.transport.loseConnection()
			return

		self.state = self.STATE_READY
		self.factory.madeConnection(self.transport.addr[0])

	def dataReceived(self, buf):
		if self.state == self.STATE_READY:
			self.factory.consumer.write(buf)

		self.buf += buf
		if self.state == self.STATE_WAIT_AUTHOK:
			self._waitAuthOk()
		elif self.state == self.STATE_WAIT_CONNECTOK:
			self._waitConnectOk()
