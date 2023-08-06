from Testing import ZopeTestCase
from transaction import commit

# Import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five import zcml

# iqpp.plone.rotating imports
import iqpp.plone.rotating

setupPloneSite()

class RotatingLayer(PloneSite):

    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        portal = app.plone

        zcml.load_config('configure.zcml', iqpp.plone.rotating)
        
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-iqpp.plone.rotating:iqpp.plone.rotating')        

        commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        pass

class RotatingTestCase(PloneTestCase):
    """Base class for integration tests for the 'iqpp.plone.rotating' product.
    """
    layer = RotatingLayer
    
class RotatingFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'iqpp.plone.rotating' product.
    """
    layer = RotatingLayer  