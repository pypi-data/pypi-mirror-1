#! /usr/bin/env python

# Twisted Imports
from twisted.internet import reactor
from twisted.web import xmlrpc, server
from twisted.web.xmlrpc import XMLRPC
from time import time
from copy import copy
from exceptions import KeyError
CLEANUP_INTERVAL = 10.0

class ChatRoom(object):
	"""Represents a chatroom
	""" 
	
	def __init__(self):
		"""
		"""
		self.aliveUsers = set()
		self.lastAccess = dict() 
		self.messages = dict() 
		self.lastUserChange = time()
		
	def login(self,userID,now):
		"""
		"""
		self.lastUserChange = now
		self.lastAccess[userID] = now
		self.aliveUsers.add(userID)
		messTss = self.messages.keys()
		messTss.sort()
		messages=[self.messages[ts] for ts in messTss]
		return [list(self.aliveUsers),messages]
			
	def logout(self,userID,now):
		"""
		"""
		try:
			del self.lastAccess[userID]
		finally:
			self.aliveUsers.remove(userID)
			self.lastUserChange = now

		
	def cleanup(self,now,cleanupInterval):
		"""
		"""
		
		messKeys = copy(self.messages.keys())
		for tstamp in messKeys:
			if (now-tstamp)>=cleanupInterval:
				del self.messages[tstamp]
		users  = copy(self.lastAccess.keys())
		for user in users:
			if (now-self.lastAccess[user])>=cleanupInterval:
				del self.lastAccess[user]
				self.aliveUsers.remove(user)
				self.lastUserChange = now
				
	def update(self,userID,now):
		"""
		"""
		
		users = []
		try:
			if self.lastUserChange>self.lastAccess[userID]:
				users = list(self.aliveUsers)
		except KeyError:
			return self.login(userID,now)
		tss=[ts for ts in self.messages.keys() if ts>self.lastAccess[userID]]
		tss.sort()
		messages = [self.messages[ts] for ts in tss]
		self.lastAccess[userID] = now
		return [users,messages]

	def sendMessage(self,userID,message,now):
		"""
		"""
		self.messages[now] = message
		return self.update(userID,now)
			

class MessageKeeper(XMLRPC):
	"""
	"""

	def __init__(self):
		XMLRPC.__init__(self)
		self.chatrooms = dict() 
		reactor.callLater(CLEANUP_INTERVAL, self.cleanup)

	def cleanup(self):
		"""
		"""
		now = time()
		for room in self.chatrooms:
			self.chatrooms[room].cleanup(now,CLEANUP_INTERVAL)	
		reactor.callLater(CLEANUP_INTERVAL, self.cleanup)
		

	def xmlrpc_login(self,chatUID,userID):
		"""
		"""
		now = time()
		try:
			users = self.chatrooms[chatUID].login(userID,now)
		except KeyError:
			self.chatrooms[chatUID] = ChatRoom()
			users = self.chatrooms[chatUID].login(userID,now)
		return users

	def xmlrpc_update(self,chatUID,userID):
		"""
		"""
		now = time()
		try:
			return self.chatrooms[chatUID].update(userID,now)
		except KeyError:
			self.chatrooms[chatUID] = ChatRoom()
			return self.chatrooms[chatUID].update(userID,now)
		
	def xmlrpc_sendMessage(self,chatUID,userID,message):
		now = time()
		return self.chatrooms[chatUID].sendMessage(userID,message,now)
			
		
	def xmlrpc_logout(self,chatUID,userID):
		"""
		"""
		now = time()
		self.chatrooms[chatUID].logout(userID,now)
		return ""
				
if __name__ == '__main__':
	
	theKeeper = MessageKeeper()
	reactor.listenTCP(8000, server.Site(theKeeper))
	reactor.run() 
