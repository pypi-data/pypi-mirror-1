from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface

class IThreeColorsTheme(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 Skin browser layer.
    """
    
class IThreeColorsThemedynamicImages(Interface):
    """
      Marker interface for ThreeColorsThemedynamicImages
    """
    
    def getIconsColor(self):
        """
        Render some colors of a phantasy skin
        used to change icons color
        """
        
    def getCollapsedIcon(self):
        """
        Icon rendered in phantasyskin context or portal context
        """
        
    def getExpandedIcon(self):
        """
        Icon rendered in phantasyskin context or portal context
        """     