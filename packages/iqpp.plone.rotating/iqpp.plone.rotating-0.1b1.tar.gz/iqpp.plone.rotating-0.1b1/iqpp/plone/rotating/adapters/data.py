# zope imports
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts

# ATContentTypes
from Products.ATContentTypes.interface import IATDocument
from Products.ATContentTypes.interface import IATImage

# iqpp.plone.rotating
from iqpp.plone.rotating.interfaces import IData

class Data:
    """Base adapter, which provides IData for arbitrary objects.
    """
    implements(IData)
    adapts(Interface)    
    
    def __init__(self, context):
        """
        """
        self.context = context

    def getContent(self):
        """
        """
        return self.context.Description()

    def getFooter(self):
        """
        """
        return None

    def getTitle(self):
        """
        """
        return self.context.Title()
        
    def getURL(self):
        """
        """    
        return self.context.absolute_url()
        
class ImageData(Data):
    """Adapter, which provides IData for ATDocuments.
    """
    implements(IData)
    adapts(IATImage)

    def getContent(self):
        """
        """
        return self.context.getTag()