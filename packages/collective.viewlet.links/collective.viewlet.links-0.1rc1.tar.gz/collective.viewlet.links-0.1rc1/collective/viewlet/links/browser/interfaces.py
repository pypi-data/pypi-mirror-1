from plone.theme.interfaces import IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    If you need to register a viewlet only for the current
    product, this interface must be it's layer.
    """

