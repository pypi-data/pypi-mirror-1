from zope.interface import implements
from zope.component import getMultiAdapter

from qi.jabberHelpdesk.interfaces import IMessageHandler
#from zope.component import getUtility
from xmlrpclib import Server
from Products.Five.browser import BrowserView

class HelpdeskXMLRPC(BrowserView):
	"""
	"""
	implements(IMessageHandler)
	
	def __init__(self, context, request):
		""" init view """
		self.context = context
		self.request = request
		settings =	getMultiAdapter((context,request), name="helpdesk_settings")
		self.rpcserver = Server('http://%s:%i'%(settings.xmlrpc_host,settings.xmlrpc_port))
	def userLogin(self,botID,userID,name,subject):
		"""
		"""
		(result,agent)= self.rpcserver.userLogin(botID,userID,name,subject)
		if result:
			return agent
		raise Exception("No agent available")
			
	def userLogout(self,botID,userID):
		"""
		"""
		self.rpcserver.userLogout(botID,userID)
		
	def sendUserMessage(self,botID,userID,message):
		"""
		"""		
		result= self.rpcserver.sendUserMessage(botID,userID,message)
		if not result:
			raise Exception("You have been disconnected")
			
	def getUserMessages(self,botID,userID):
		"""
		"""
		(result,messages,files) = self.rpcserver.getUserMessages(botID,userID)
		if result:
			return [messages,files]
		raise Exception("You have been disconnected")
	
	def getAliveAgents(self,botID):
		"""
		"""
		return self.rpcserver.getAliveContacts(botID)

	def getAvailableAgents(self,botID):
		"""
		"""
		return self.rpcserver.getAvailableContacts(botID)

	def getHelpdeskAgents(self,botJID):
		"""
		"""
		return self.rpcserver.getContacts(botJID)
		
	def getAgentAvatarB64(self,botID,userID):
		"""
		"""
		return self.rpcserver.getContactAvatarB64(botID,userID)

	def getAgentVCard(self,botID,userID):
		"""
		"""
		return self.rpcserver.getContactVCard(botID,userID)

	def loadBot(self,botID,botPass,persistent):
		"""
		"""
		return self.rpcserver.loadBot(botID,botPass,persistent)
		
	def addAgent(self,botJID,agentId):
		"""
		"""
		return self.rpcserver.addContact(botJID,agentId)
	
	def removeAgent(self,botJID,agentId):
		"""
		"""
		return self.rpcserver.delContact(botJID,agentId)
	
	def addBot(self,botJID,botPass):
		"""
		"""
		return self.rpcserver.addUser(botJID,botPass)

	def removeBot(self,botJID):
		"""
		"""
		return self.rpcserver.delUser(botJID)
