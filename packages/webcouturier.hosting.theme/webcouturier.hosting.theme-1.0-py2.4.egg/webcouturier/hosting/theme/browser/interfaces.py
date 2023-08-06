from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """
    
class IThemeTablelessSpecific(IThemeSpecific):
    """Marker interface that defines a Zope 3 skin layer.
       This one is used for tableless version only of the skin
    """    
