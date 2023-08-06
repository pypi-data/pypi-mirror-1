from qi.xmpp.client.client import JabberClient
from twisted.words.protocols.jabber import jid
from twisted.words.xish.domish import Element
from twisted.words.xish import xpath
import qi.xmpp.client.ns as ns
from twisted.internet import reactor
import qi.xmpp.client.xmppComm as xmppComm
class AdminSession(JabberClient):
	"""
	"""
	
	def __init__(self,myjid,sessionManager):
		"""
		"""
		JabberClient.__init__(self,myjid)		
		self.server = jid.JID(myjid).userhost().split('@')[1]
		self.sm = sessionManager
		
		

	def addUser(self,userjid,userpass):
		"""
		"""
		
		def rcvdAddUserForm(iq):
			sessionID = iq.command["sessionid"]
			if sessionID:
				newiq = Element(("","iq"))
				newiq["from"] = self.jabberID.full()
				newiq["to"] = self.server
				newiq["type"] = "set"

				command = newiq.addElement((ns.NS_COMMANDS,"command"))
				command["node"] = ns.NS_ADMIN+"#add-user"
				command["sessionid"] = sessionID

				x = command.addElement("x",ns.NS_XDATA)
				x["type"]="submit"
				field = x.addElement("field")
				field["type"]="hidden"
				field["var"]="FORM_TYPE"
				field.addElement("value",content=ns.NS_ADMIN)
				nodes = xpath.queryForNodes('/iq/command/x/field',iq)
				for node in nodes:
					var = node["var"]
					if var == "accountjid":
						field = x.addElement("field")
						field["var"] = var
						field.addElement("value",content=userjid)
					elif var in ["password","password-verify"]:
						field = x.addElement("field")
						field["var"] = var
						field.addElement("value",content=userpass)
					elif var == "FORM_TYPE":
						pass
					else:
						field.addElement("value")
				
				addResult = xmppComm.sendIq(self,newiq)
				return addResult.addCallback(rcvdAddUserResult)
						
			else:
				return None

		def rcvdAddUserResult(iq):
			if xpath.matches('/iq/command[@status="completed"]',iq):
				return userjid
			else:
				return None
		iq = Element(("","iq"))
		iq["from"] = self.jabberID.full()
		iq["to"] = self.server
		iq["type"] = "set"
		iq["xml:lang"]="en"
		command = iq.addElement((ns.NS_COMMANDS,"command"))
		command["action"]="execute"
		command["node"] = ns.NS_ADMIN+"#add-user"
		fd = xmppComm.sendIq(self,iq)
		fd.addCallback(rcvdAddUserForm)
		return fd
		
	def delUser(self,userjid):
		"""
		"""
		
		def rcvdDelUserForm(iq):			
			sessionID = iq.command["sessionid"]
			if sessionID:
			
				newiq = Element(("","iq"))
				newiq["from"] = self.jabberID.full()
				newiq["to"] = self.server
				newiq["type"] = "set"

				command = newiq.addElement((ns.NS_COMMANDS,"command"))
				command["node"] = ns.NS_ADMIN+"#delete-user"
				command["sessionid"] = sessionID
	
				x = command.addElement("x",ns.NS_XDATA)
				x["type"]="submit"
				field = x.addElement("field")
				field["type"]="hidden"
				field["var"]="FORM_TYPE"
				field.addElement("value",content=ns.NS_ADMIN)
				
				field = x.addElement("field")
				
				field["var"] = "accountjids"
				field.addElement("value",None,content=userjid)
				
				delResult = xmppComm.sendIq(self,newiq)
				delResult.addCallback(rcvdDelUserResult)
				return delResult
			else: 
				return False
				
		def rcvdDelUserResult(iq):

			if xpath.matches('/iq/command[@status="completed"]',iq):
				return True
			else:
				return False
		def delUserFromServer():
			iq = Element(("","iq"))
			iq["from"] = self.jabberID.full()
			iq["to"] = self.server
			iq["type"] = "set"
			command = iq.addElement((ns.NS_COMMANDS,"command"))
			command["action"]="execute"
			command["node"] = ns.NS_ADMIN+"#delete-user"
			fd = xmppComm.sendIq(self,iq)
			fd.addCallback(rcvdDelUserForm)
			return fd
						
		if userjid in self.sm.sessions.keys():
			self.sm.sessions[userjid].logout()
			self.sm.delSession(userjid)
			d = delUserFromServer()
			return d
		else:
			d = delUserFromServer()
			return d
	def getNoRegisteredUsers(self):
		def rcvdResult(iq):
			node = xpath.queryForNodes("/iq/command/x/field[@var='registeredusersnum']",iq)
			if node:
				return int(node[0].value.__str__())
		iq = Element(("","iq"))
		iq["from"] = self.jabberID.full()
		iq["to"] = self.server
		iq["type"] = "set"
		command = iq.addElement((ns.NS_COMMANDS,"command"))
		command["action"]="execute"
		command["node"] = ns.NS_ADMIN+"#get-registered-users-num"
		d = xmppComm.sendIq(self,iq)
		d.addCallback(rcvdResult)
		return d