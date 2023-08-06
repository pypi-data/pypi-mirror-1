from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from qi.LiveChat.browser.ILiveChatView import ILiveChatView

class LiveChatView(BrowserView):
	"""
	"""
	implements(ILiveChatView)
	__call__ = ViewPageTemplateFile('livechat_view.pt')
	
	def __init__(self,context,request):
		BrowserView.__init__(self,context,request)
		self.mt = getToolByName(context,"portal_membership")

	def getUser(self):
		"""
		"""
		return self.mt.getAuthenticatedMember()
	
	def isAnonymous(self):
		"""
		"""
		portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
		if portal_state.anonymous():
			return True
		return False