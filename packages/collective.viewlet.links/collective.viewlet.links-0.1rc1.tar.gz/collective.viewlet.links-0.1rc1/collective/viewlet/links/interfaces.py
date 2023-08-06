from zope.interface.interface import Interface
from zope import schema

from collective.viewlet.links.config \
     import LinksMessage as _


class ICanDefineLinks(Interface):
    """Marker interface for objects that can define custom links
    """

class ILink(Interface):
    """representing a link.
    """

    title = schema.TextLine(title = _(u"Link Title"))
    url = schema.ASCIILine(title = _(u"Link URL"))


class ILinkDataAnnotation(Interface):
    """Annotation that stores Link information on objects implementing
    ICanDefineLinks.

    inheritLinks = Bool #could be future feature
    """

    links = schema.List(title = _(u"Links"),
                        value_type = schema.Object(title = _(u"Link"),
                                                   schema = ILink,
                                                   ),
                        default = [],
                        )


    #links = schema.List(
    #    title=_('Links'),
    #    description=_('List the link name and url here'),
    #    value_type=schema.Tuple(
    #    min_length=2,
    #    max_length=2,
    #    value_type=schema.TextLine()),
    #    required=False,
    #    default=[])
