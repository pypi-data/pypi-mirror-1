# -*- coding: utf-8 -*-

from zope.interface import Interface

class ILiveChat(Interface):
    """
    Marker interface for LiveChat
    """

class IMessageKeeper(Interface):
	"""
	Message keeper utility interface
	"""
	def login(chatroom,user):
		"""
		"""
	
	def logout(chatroom,user):
		"""
		"""
	
	def sendMessage(chatroom,user,message):
		"""
		"""
		
	def update(chatroom,user):
		"""
		"""
		
		