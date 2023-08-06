from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Twinapex Theme" theme, this interface must be its layer
       (in skin/viewlets/configure.zcml).
    """

class INavManager(IViewletManager):
    """ Market """