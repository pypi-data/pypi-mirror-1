from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IAndreas09Footer(IViewletManager):
    """A viewlet manager for wrapping the footer into a <div id="footer"> tag.
    """
