from Products.CMFCore.permissions import setDefaultRoles
from collective.viewlet.links import config


#register our permission within zope2 instance root
#in rolemap.xml we map it to roles on the plone site level when installing the product
setDefaultRoles(config.MANAGE_LINKS_PERMISSION, ('Manager',))

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
