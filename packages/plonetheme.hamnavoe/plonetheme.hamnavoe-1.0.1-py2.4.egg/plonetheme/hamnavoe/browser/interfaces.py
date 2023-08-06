from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ISplashImage(Interface):
    """ Generates Hamnavoe splash image """
    
    def getSplashImage(self):
        """
          Get the splash image
        """
        
class IStrapline(Interface):
    """ Make the site strapline """
    
    def getStrapline(self):
        """
           Make the strapline
        """