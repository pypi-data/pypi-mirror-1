from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer bound to a Skin
       Selection in portal_skins.
       If you need to register a viewlet only for the "Web Couturier City Theme"
       skin, this is the interface that must be used for the layer attribute
       in Theme1/browser/configure.zcml.
    """