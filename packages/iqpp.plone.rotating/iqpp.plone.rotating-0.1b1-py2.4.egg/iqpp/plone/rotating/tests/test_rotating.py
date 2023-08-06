# Zope imports
from AccessControl import Unauthorized
from DateTime import DateTime

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility, queryUtility

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# AdvancedQuery imports
from Products.AdvancedQuery import In, Eq, Ge, Le

# test imports
from base import RotatingTestCase

# iqpp.rating imports
from iqpp.plone.rotating.interfaces import IRotating
from iqpp.plone.rotating.interfaces import IRotatingOptions

class TestRotating(RotatingTestCase):
    """
    """
    def afterSetUp(self):
        """
        """
        self.loginAsPortalOwner()
        
        self.folder.invokeFactory("Topic", id="topic")
        self.topic = self.folder.topic

        crit = self.topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Image')
            
        self.folder.invokeFactory("Image", id="test_1")
        self.folder.invokeFactory("Image", id="test_2")
        self.folder.invokeFactory("Image", id="test_3")
        self.folder.invokeFactory("Image", id="test_4")

    def testRotating_1(self):
        """Is always a item found?
        """
        # NOTE: by default already displayed items are displayed again.
        r = IRotating(self.topic)
        for i in range(1, 10):
            self.failIf(r.getItem() is None)
                
    def testRotatingLimit(self):
        """Test limit
        """
        r = IRotating(self.topic)        
        items = r.getItems(limit=4)
        self.failUnless(len(items), 4)
    
        # All found items have to be found in topic
        for item in items:
            self.failUnless(item["id"] in [o.id for o in self.topic.queryCatalog()])
    
        # All existing objects has to be found in the result
        item_ids = [item["id"] for item in items]
        for id in ("test_1", "test_2", "test_3", "test_4"):
            self.failUnless(id in item_ids)
    
    def testRotatingSelected_1(self):
        """No reset
        """
        ro = IRotatingOptions(self.topic)
        ro.setOptions(
            show_already_selected=False,
            reset_already_selected=False)

        r = IRotating(self.topic)
        
        # show_already_selected = False means we get each item only once
        items = []
        for i in range(0, 4):
            item = r.getItem()
            items.append(item)
        
        # Now all existing objects has to be found in the result ...
        item_ids = [item["id"] for item in items]
        for id in ("test_1", "test_2", "test_3", "test_4"):
            self.failUnless(id in item_ids)
    
        # ... and since all are found (marked as selected) next getItems should
        # return None
        
        item = r.getItem()
        self.failUnless(item is None)

        items = r.getItems()
        self.failUnless(items == [])
    
    def testRotatingSelected_2(self):
        """Reset
        """
        ro = IRotatingOptions(self.topic)        
        ro.setOptions(
            show_already_selected=False,
            reset_already_selected=True)

        r = IRotating(self.topic)
                
        # show_already_selected = False means get each item only once
        items = []
        for i in range(0, 4):
            item = r.getItem()
            items.append(item)
    
        # Now all existing objects has to be found in the result 
        item_ids = [item["id"] for item in items]
        for id in ("test_1", "test_2", "test_3", "test_4"):
            self.failUnless(id in item_ids)
        
        # But as we reset already found objects ... 
        items = []
        for i in range(0, 4):
            item = r.getItem()
            items.append(item)
    
        # ... all existing objects has to be found in the result again
        item_ids = [item["id"] for item in items]    
        for id in ("test_1", "test_2", "test_3", "test_4"):
            self.failUnless(id in item_ids)
        
    def testRotatingDateUpdate_1(self):
        """
        """
        # We set the update intervall to one hour
        ro = IRotatingOptions(self.topic)
        ro.setOptions(update_intervall = 1)

        r = IRotating(self.topic)

        result_1 = r.getItem()
        self.failIf(result_1 is None)

        # So the next calls to getItem has to be return always the same object.
        for i in range(0, 10):
            result_2 = r.getItem()
            self.failUnless(result_1["id"] == result_2["id"])
        
                        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRotating))
    return suite