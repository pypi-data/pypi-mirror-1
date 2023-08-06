PRESENCE = '/presence' # this is an global xpath query to use in an observer
MESSAGE	 = '/message'  # message xpath 
IQ		 = '/iq'	   # iq xpath
ANYTHING = '/*'

NS_CLIENT = 'jabber:client'

NS_XMPP_STANZAS  = "urn:ietf:params:xml:ns:xmpp-stanzas"
NS_PING			 = "urn:xmpp:ping"
NS_DISCO         = "http://jabber.org/protocol/disco"
NS_DISCO_ITEMS   = NS_DISCO + "#items"
NS_DISCO_INFO    = NS_DISCO + "#info"
NS_COMMANDS      = "http://jabber.org/protocol/commands"
NS_ADMIN		 = "http://jabber.org/protocol/admin"
NS_CAPS          = "http://jabber.org/protocol/caps"
NS_SUBSYNC       = "http://delx.cjb.net/protocol/roster-subsync"
NS_MUC           = "http://jabber.org/protocol/muc"
NS_MUC_USER      = NS_MUC + "#user"
NS_FEATURE_NEG   = "http://jabber.org/protocol/feature-neg"
NS_SI            = "http://jabber.org/protocol/si"
NS_FT            = "http://jabber.org/protocol/si/profile/file-transfer"
NS_S5B           = "http://jabber.org/protocol/bytestreams"
NS_IBB           = "http://jabber.org/protocol/ibb"
NS_IQGATEWAY     = "jabber:iq:gateway"
NS_IQVERSION     = "jabber:iq:version"
NS_IQREGISTER    = "jabber:iq:register"
NS_IQROSTER      = "jabber:iq:roster"
NS_IQAVATAR      = "jabber:iq:avatar"
NS_IQOOB         = "jabber:iq:oob"
NS_XOOB          = "jabber:x:oob"
NS_XCONFERENCE   = "jabber:x:conference"
NS_XEVENT        = "jabber:x:event"
NS_XDELAY        = "jabber:x:delay"
NS_XAVATAR       = "jabber:x:avatar"
NS_XDATA         = "jabber:x:data"
NS_STORAGEAVATAR = "storage:client:avatar"
NS_XVCARDUPDATE  = "vcard-temp:x:update"
NS_VCARDTEMP     = "vcard-temp"


XP_COMMANDS		 = "/iq/query/feature[@var='http://jabber.org/protocol/commands']"