# Zope imports
from zope.interface import Interface
from zope import schema

# iqpp.plone.rotating
from iqpp.plone.rotating.config import _

class IRotating(Interface):
    """Provides methods to get rotating items.
    """
    def getItem():
        """Returns next item.
        """
        
    def getItems():
        """Returns next items.
        """

    def setOptions(**kwargs):
        """Sets options.
        """
        
class IData(Interface):
    """Provides methods to get same kind of data from arbitrary objects.
    """
    def getContent(self):
        """Returns generic content of the item.
        """        

    def getFooter():
        """Returns the footer of the item.
        """                
        
    def getTitle():
        """Returns the title of the item.
        """

    def getURL():
        """Returns the URL of the item.
        """
        
class IRotatingOptions(Interface):
    """
    """
    show_already_selected = schema.Bool(
        title=_(u'Show Already Selected'),
        description=_(u'If checked, already selected items within "Path" can be displayed again. If unchecked all items within "Path" are displayed only once.'),
        required=False,)

    reset_already_selected = schema.Bool(
        title=_(u'Reset Selected'),
        description=_(u'If checked already selected items within "Path" will be reset if all items has been displayed.'),
        required=False,)

    update_intervall = schema.Int(
        title=_(u'Update Intervall'),
        description=_(u'Within this intervall the same object are returned.'),
        default=0,
        required=True)

    set_to_midnight = schema.Bool(
        title=_(u'Set To Midnight'),
        description=_(u'If checked "Last Update" is always set to midnight. This only makes sense if "Update Intervall" is set to an multiple of 24 hours.'),
        required=False)