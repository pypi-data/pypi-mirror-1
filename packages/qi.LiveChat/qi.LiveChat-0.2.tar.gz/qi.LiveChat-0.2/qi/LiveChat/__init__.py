# XXX imports went into try so that livechat_server would run without needing to have full zope environment...
# There must be a cleaner way of doing this.
try:
	from config import *
	from zope.i18nmessageid import MessageFactory
	from Products.CMFCore import utils
	from Products.Archetypes import atapi
	LiveChatMessageFactory = MessageFactory('qi.LiveChat')
except:
	pass

def initialize(context):
	import content.LiveChat

	content_types, constructors, ftis = atapi.process_types(
		atapi.listTypes(config.PROJECTNAME),
		config.PROJECTNAME)

	for atype, constructor in zip(content_types, constructors):
		utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
			content_types	   = (atype,),
			permission		   = config.ADD_PERMISSIONS[atype.portal_type],
			extra_constructors = (constructor,),
			).initialize(context)
