from qi.LiveChat.kss.ILiveChatKSSCommands import ILiveChatKSSCommands
from kss.core import CommandSet
from zope import interface

class LiveChatKSSCommands(CommandSet):
	interface.implements(ILiveChatKSSCommands)
	
	def resetScrollbar(self, selector):
		command = self.commands.addCommand('resetScrollbar', selector)
	def resetInput(self, selector):
		command = self.commands.addCommand('resetInput', selector)
