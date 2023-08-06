
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import \
     ViewPageTemplateFile
from zope.component import getUtility
from Products.Five.security import checkPermission
from Products.CMFPlone.utils import safe_unicode
from collective.viewlet.links.interfaces import ILinkDataAnnotation
from collective.viewlet.links.interfaces import ICanDefineLinks
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from collective.viewlet.links.config import MANAGE_LINKS_PERMISSION_Z3
from collective.viewlet.links.config \
     import LinksMessage as _
from Acquisition import aq_inner

class LinksViewlet(ViewletBase):
    """A custom viewlet that shows a list of links
    """
    render = ViewPageTemplateFile('links_viewlet.pt')


    def getNextLinkSource(self, context):
        """returns the next object up in the acquisition hierarchy that actually defines some links.
        """

        provider = self.getNextLinkProvider(context)
        while len(ILinkDataAnnotation(provider).links) == 0:
            if IPloneSiteRoot.providedBy(provider):
                return provider
            provider = self.getNextLinkProvider(provider.aq_parent)

        return provider



    def getNextLinkProvider(self, context):
        """returns the next object providing ICanDefineLinks up the aquisition hierarchy.
        """

        while not ICanDefineLinks.providedBy(context):
            #this will walk up until plonesite (which implements this interface anyway)
            context = context.aq_parent

        return context


    def update(self):
        super(LinksViewlet, self).update()
        self.actions = []
        context = aq_inner(self.context)


        # check if local links are allowed in the configuration (planned for future release),
        # otherwise we can just return links for the plone-site


        linkSource = self.getNextLinkSource(context)
        self.links = ILinkDataAnnotation(linkSource).links

        #link for managing currently displayed links
        if checkPermission(MANAGE_LINKS_PERMISSION_Z3, linkSource):
            self.actions.append(dict(title = _(u"Manage links"),
                                   url = linkSource.absolute_url() + '/@@manage-links',
                                   ))
        #link to the nearest context that we may define custom links for
        nextProvider = self.getNextLinkProvider(context)
        if nextProvider != linkSource and checkPermission(MANAGE_LINKS_PERMISSION_Z3, nextProvider):
            self.actions.append(dict(title = _(u"Set links for ${context}",
                                             mapping={'context': safe_unicode(nextProvider.title)}),
                                   url = nextProvider.absolute_url() + '/@@manage-links'))


