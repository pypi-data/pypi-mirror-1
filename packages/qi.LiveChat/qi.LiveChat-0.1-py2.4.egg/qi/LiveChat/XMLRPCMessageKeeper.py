from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite
from qi.LiveChat.interfaces import IMessageKeeper
from xmlrpclib import Server

class XMLRPCMessageKeeper(object):
	"""
	"""
	implements(IMessageKeeper)
	def __init__(self):
		"""
		"""
		self.rpcserver = Server('http://localhost:8000')		
		
	def login(self,chatUID,userID):
		"""
		"""
		return self.rpcserver.login(chatUID,userID)
			
	def logout(self,chatUID,userID):
		"""
		"""
		self.rpcserver.logout(chatUID,userID)
		
	def sendMessage(self,chatUID,userID,message):
		"""
		"""
		return self.rpcserver.sendMessage(chatUID,userID,message)

	def update(self,chatUID,userID):
		"""
		"""
		return self.rpcserver.update(chatUID,userID)
		