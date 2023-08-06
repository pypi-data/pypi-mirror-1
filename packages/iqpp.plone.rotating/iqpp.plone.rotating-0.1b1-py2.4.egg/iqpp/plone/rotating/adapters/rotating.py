# ZODB imports
from persistent.dict import PersistentDict

# python imports
from datetime import datetime
from datetime import timedelta
import random

# zope imports
import pytz
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts

# from iqpp.plone.rotating import
from iqpp.plone.rotating.interfaces import IData
from iqpp.plone.rotating.interfaces import IRotating
from iqpp.plone.rotating.interfaces import IRotatingOptions

KEY = "iqpp.plone.rotating"

class TopicRotating(object):
    """Implements IRotating for topics.
    """
    implements(IRotating)
    adapts(Interface)

    def __init__(self, context):
        """
        """
        self.context = context
        annotations = IAnnotations(context)
        temp = annotations.get(KEY)
        
        if temp is None:
            temp = annotations[KEY] = PersistentDict()
            temp["already_selected"] = []
            temp["last_update"] = None
                            
        self.annotations = temp

    def getItem(self):
        """
        """
        items = self.getItems(1)
        try:
            return items[0]
        except (IndexError, TypeError):
            return None
            
    def getItems(self, limit=1):
        """
        """
        options = IRotatingOptions(self.context)
        
        time_zone = pytz.UTC
        now = datetime.now(time_zone)        
        delta = timedelta(hours=options.update_intervall)
        
        last_update = self.annotations["last_update"]
        if last_update is None or \
           self.annotations["current_items"] == [] or \
           now - last_update >= delta:
        
            # Get requested objects
            brains = self.context.queryCatalog()
            
            # Reset selected objects (if requested)
            if options.show_already_selected == False and \
               options.reset_already_selected == True and \
                len(self.annotations["already_selected"]) >= len(brains):
                    self.annotations["already_selected"] = []
            
            # Omit already selected objects (if requested)
            result = []
            if options.show_already_selected == True:
                result = list(brains)
            else:
                for brain in brains:
                    if brain.UID not in self.annotations["already_selected"]:
                        result.append(brain)
            
            # Nothing found
            if len(result) == 0:
                return []

            # Get random objects
            random.shuffle(result)
            result = result[0:limit]
            
            # Save already selected objects (if requested)
            if options.show_already_selected == False:
                uids = [b.UID for b in result]
                self.annotations["already_selected"].extend(uids)

            if options.set_to_midnight == True:
                y, m, d = now.timetuple()[0:3]
                self.annotations["last_update"] = datetime(y, m, d, tzinfo=time_zone)
            else:
                self.annotations["last_update"] = now

            # Store items
            items = []
            for item in result:
                data = IData(item.getObject())
                items.append({
                    "id"          : item.getId,
                    "type"        : item.portal_type,
                    "title"       : data.getTitle(),
                    "description" : item.Description,
                    "content"     : data.getContent(),
                    "footer"      : data.getFooter(),
                    "url"         : data.getURL(),
                })
                
            self.annotations["current_items"] = items
        
        return self.annotations["current_items"]
