from zope.interface.interface import Interface
from zope import schema

from z3c.form.field import Fields
from z3c.form import util

from plone.app.z3cform.layout import wrap_form
from collective.viewlet.links.interfaces import ILinkDataAnnotation
from collective.viewlet.links.annotations import Link
from zope.interface.declarations import implements
from collective.viewlet.links.interfaces import ICanDefineLinks
from collective.viewlet.links.annotations import LinkValidator
from collective.viewlet.links.interfaces import ILink
from zope.component._declaration import adapts
from z3c.form import button
from z3c.form.form import EditForm
from z3c.form import validator
from zope.component import provideAdapter
from collective.viewlet.links.config \
     import LinksMessage as _



class ILinkForm(Interface):
    """Interface specifying fields for the contact form.
    """

    links = schema.Text(title = _(u"Links"),
                      description = _(u"One entry per line 'Linktitle;url' (semicolon)"),
                      required = False)


class LinkForm(EditForm):

    fields = Fields(ILinkForm)

    successMessage = _(u'Links saved.')
    noChangesMessage = _('No changes were applied.')
    formErrorsMessage = _('There were some errors.')

class FormContextAdapter(object):
    """can obtain and store ILinkForm data on the context.
    """
    implements(ILinkForm)
    adapts(ICanDefineLinks)

    def __init__(self, context):
        self.context = context

    def _get_links(self):
        links = ILinkDataAnnotation(self.context).links

        return u'\r\n'.join([u"%s;%s" %(link.title, link.url) for link in links])

    def _set_links(self, value):

        if value is None:
            #blank form, delete links
            ILinkDataAnnotation(self.context).links = []
            return

        links = []
        for line in value.split('\r\n'):
            if line != '':
                #skip blank lines
                title, url = line.split(';')
                links.append(Link(title,url.encode('ascii')))

        ILinkDataAnnotation(self.context).links = links

    links = property(_get_links, _set_links)


WrappedLinkForm = wrap_form(LinkForm)

validator.WidgetsValidatorDiscriminators(
    LinkValidator,
    schema=util.getSpecification(ILinkForm, force=True))

provideAdapter(LinkValidator)

