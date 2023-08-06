from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """ Marker interface that defines a Zope 3 browser layer. """
    
class IAtrealThemeTopManager(IViewletManager):
    """ A viewlet manager thats sits above content and column right. """
