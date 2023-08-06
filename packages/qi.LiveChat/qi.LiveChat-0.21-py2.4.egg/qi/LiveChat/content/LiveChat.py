from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
from qi.LiveChat.interfaces import ILiveChat
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, ATContentTypeSchema
from Products.ATContentTypes.content.base import ATCTContent
from qi.LiveChat.config import PROJECTNAME
schema = Schema((
),
)

LiveChat_schema = ATContentTypeSchema.copy() + \
    schema.copy()

class LiveChat(ATCTContent):
    """
    """
    implements(ILiveChat)
    security = ClassSecurityInfo()
    schema = LiveChat_schema

    def __init__(self, *args, **kwargs):
        """
        """
        ATCTContent.__init__(self,*args, **kwargs)

registerType(LiveChat, PROJECTNAME)
