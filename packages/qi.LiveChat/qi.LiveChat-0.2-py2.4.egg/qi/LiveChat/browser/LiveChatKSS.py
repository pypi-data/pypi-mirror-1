from zope.component import getUtility
from kss.core import KSSView
from DateTime import DateTime
from elementtree.ElementTree import XML as parseET
from Products.CMFCore.utils import getToolByName 
from Products.CMFDefault.utils import scrubHTML
from emoticons	import replaceEmoticons
from plone.intelligenttext.transforms import convertHtmlToWebIntelligentPlainText, convertWebIntelligentPlainTextToHtml
from qi.LiveChat.interfaces import IMessageKeeper

from qi.LiveChat import LiveChatMessageFactory as _
class LiveChatKSS(KSSView):
	"""
	"""
	def __init__(self, *args):
		KSSView.__init__(self, *args)
		self.chat = self.context.aq_inner
		self.core = self.getCommandSet('core')
		self.lckss = self.getCommandSet('livechat')
		self.plone = self.getCommandSet('plone')
		self.mt = getToolByName(self.chat,"portal_membership")
		self.mk = getUtility(IMessageKeeper)
		self.uid = self.chat.UID()

	def login(self):
		"""
		A user connects to the chat room.
		"""
	
		user = str(self.mt.getAuthenticatedMember())
		try:
			(users,messages) = self.mk.login(self.uid,user)
		except:
			return self._connectionError()
		self._updateUsers(users)
		self._updateMessages(messages)
		self.core.focus("#msgInput")
		return self.render()
	
	def logout(self):
		"""
		User log outs from the chat
		"""
		user = str(self.mt.getAuthenticatedMember())
		self.mk.logout(self.uid,user)	
		return self.render()
	
	def ping(self,message=None):
		"""
		"""
		user = str(self.mt.getAuthenticatedMember())

		if message:
			dt=DateTime()
			message = convertHtmlToWebIntelligentPlainText(message)
			message = convertWebIntelligentPlainTextToHtml(message)
			message = replaceEmoticons(message)
			time = dt.Time()
			try:
				(users,messages) = self.mk.sendMessage(self.uid,user,[time,user,message])
			except:
				return self._connectionError()
			self._updateUsers(users)
			self._updateMessages(messages)
						
			# The following is done because KSS setAttribute does not work on <input> value. 
			#self.core.setAttribute(self.core.getHtmlIdSelector('#msgInput'),'value','')
			self.lckss.resetInput("#msgInput")
			self.core.focus("#msgInput")
			return self.render()
		try:
			[users,messages] = self.mk.update(self.uid,user)
		except:
			return self._connectionError()
		
		self._updateUsers(users)
		self._updateMessages(messages)
		self.plone.issuePortalMessage(_(u""))
		return self.render()
	
	def _connectionError(self):
		"""
		"""
		self.plone.issuePortalMessage(_(u"Error connecting to Live Chat server."),'error')
		return self.render()
	
	def _updateMessages(self,messages):
		"""
		"""
		if messages:
			messagesElem = self.core.getHtmlIdSelector("messages")
			for (time,user,message)	 in messages:
				elem = '<div><span class="msg_time">%s</span><span class="msg_user">%s</span><span>%s</span></div>'%(time,user,message)
				self.core.insertHTMLAsLastChild(messagesElem, elem)
			self.lckss.resetScrollbar(messagesElem)
			
	
	def _updateUsers(self,users):
		"""
		"""
		if users:
			users.sort()
			content = ""
			for user in users:
				content=content+"<div>%s</div>"%user
			self.core.replaceInnerHTML('#loggedUsers', content)