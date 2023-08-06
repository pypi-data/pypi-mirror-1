# ZODB imports
from persistent.dict import PersistentDict
from persistent.list import PersistentList

# zope imports
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# iqpp.rating imports
from iqpp.plone.rotating.interfaces import IRotatingOptions

KEY = "iqpp.plone.rotating.options"

class RotatingOptions(object):
    """
    """
    implements(IRotatingOptions)
    adapts(Interface)
    
    def __init__(self, context):
        """
        """
        self.context = context
        annotations = IAnnotations(context)
        temp = annotations.get(KEY)
        
        if temp is None:
            temp = annotations[KEY] = PersistentDict()
            temp["current_items"] = []
            temp["update_intervall"] = 0
            temp["set_to_midnight"] = False
            temp["already_selected"] = PersistentList()
            temp["show_already_selected"] = True
            temp["reset_already_selected"] = True
                            
        self.annotations = temp
        
    def __getattr__(self, name):
        """The options form asks for an attribute for every field.
        """
        return self.annotations[name]

    def setOptions(self, **data):
        """
        """
        self.annotations.update(data)