from persistent import Persistent
from zope.interface.declarations import implements
from collective.viewlet.links.interfaces import ILinkDataAnnotation, ILink
from zope.component._api import adapts
from collective.viewlet.links.interfaces import ICanDefineLinks
from zope.schema.fieldproperty import FieldProperty
from collective.viewlet.links.config import PROJECTNAME
from zope.annotation import factory

from zope import component
import zope.interface
from z3c.form import validator
from Products.validation import validation
from Products.CMFPlone.utils import safe_unicode
from collective.viewlet.links.config \
     import LinksMessage as _

class Link(object):
    implements(ILink)

    def __init__(self, title, url):
        self.title = title
        self.url = url

    url = FieldProperty(ILink['url'])
    title = FieldProperty(ILink['title'])

class LinkException(zope.interface.Invalid): pass

class LinkValidator(validator.InvariantsValidator):
    """Validate the links
    """
    def validateObject(self, obj):
        errors = super(LinkValidator, self).validateObject(obj)

        if obj.links is None:
            # submitting an empty list (== remove all links) is allowed
            return errors

        for item in obj.links.split('\r\n'):
            if not item: continue

            #Make sure there's exactly one semicolon per line
            if item.count(';')<>1:
                errors += (LinkException(_('Use a semicolon to separate the link name from the url.  $item', mapping={'item': safe_unicode(item)})),)

            else:
                linkName, url = item.split(';')

                #Make sure we have a valid url string
                v = validation.validatorFor('isURL')
                if 1 != v(str(url)):
                    if '/' == str(url)[0]:
                        continue
                    errors += (LinkException(_(u"The URL '$url' is not valid", mapping={'url': url})),)

        return errors

class LinkDataAnnotation(Persistent):
    """see ILinkDataAnnotation

    >>> from zope.interface.verify import verifyClass, verifyObject
    >>> from collective.viewlet.links.interfaces import ILinkDataAnnotation
    >>> verifyClass(ILinkDataAnnotation, LinkDataAnnotation)
    True

    >>> from collective.viewlet.links.interfaces import ILink
    >>> ann = LinkDataAnnotation()
    >>> ann.links = [Link(u'plone','http://plone.org'),]
    >>> verifyObject(ILinkDataAnnotation, ann)
    True
    """
    implements(ILinkDataAnnotation)
    adapts(ICanDefineLinks)

    links = FieldProperty(ILinkDataAnnotation['links'])


dataKey = PROJECTNAME + '.linkannotation'
LinkDataAnnotationFactory = factory(LinkDataAnnotation, dataKey)
