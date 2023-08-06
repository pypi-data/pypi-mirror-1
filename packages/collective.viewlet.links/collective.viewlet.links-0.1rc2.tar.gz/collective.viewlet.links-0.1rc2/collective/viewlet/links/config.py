from zope.i18nmessageid import MessageFactory

PROJECTNAME = 'collective.viewlet.links'
LinksMessage = MessageFactory(PROJECTNAME)

MANAGE_LINKS_PERMISSION = "Links Viewlet: Manage links"

# the name our permission is registered for zope3 (five's permissionchecker uses this one)
MANAGE_LINKS_PERMISSION_Z3 = "collective.viewlet.links.ManageLinks"
