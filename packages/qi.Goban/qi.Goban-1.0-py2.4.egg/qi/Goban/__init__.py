"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from qi.Goban import config

from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore.permissions import setDefaultRoles

GobanMessageFactory = MessageFactory('qi.Goban')
setDefaultRoles(config.ADD_VARIATION, ('Member', 'Manager',))

def initialize(context):
	"""Intializer called when used as a Zope 2 product.
	"""
	
	from content import gogame
	
	content_types, constructors, ftis = atapi.process_types(
		atapi.listTypes(config.PROJECTNAME),
		config.PROJECTNAME)

	for atype, constructor in zip(content_types, constructors):
		utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
			content_types	   = (atype,),
			permission		   = config.ADD_PERMISSIONS[atype.portal_type],
			extra_constructors = (constructor,),
			).initialize(context)