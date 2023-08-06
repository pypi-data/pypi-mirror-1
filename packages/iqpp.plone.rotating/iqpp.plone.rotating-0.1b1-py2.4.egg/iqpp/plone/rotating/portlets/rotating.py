# zope imports
from zope.formlib import form
from zope.interface import implements
from zope import schema

# plone imports
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rotating imports
from iqpp.plone.rotating.config import _
from iqpp.plone.rotating.interfaces import IRotating

class IRotatingPortlet(IPortletDataProvider):
    """
    """
    name = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the portlet'),
        required=True,
        default=u"Title")
    
    path = schema.TextLine(
        title=_(u'Path To Folder'),
        description=_(u'The source folder.'),
        required=True,
        default=u"")

    limit = schema.Int(
        title=_(u'Number of objects to display'),
        description=_(u'How many objects to list.'),
        required=True,
        default=1)

class Assignment(base.Assignment):
    """
    """
    implements(IRotatingPortlet)

    def __init__(self, name=u"Rotating Objects", path=u"", limit=1):
        """
        """
        self.name  = name          
        self.path  = path
        self.limit = limit

    @property
    def title(self):
        return _(u"Rotating")
        
class Renderer(base.Renderer):
    """
    """
    render = ViewPageTemplateFile('rotating.pt')
    
    def update(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")            
        if mtool.checkPermission("Manage portal", self.context):        
            self.isNoManager = False
        else:
            self.isNoManager = True
            
    def getRotatingObjects(self):
        """
        """
        path = self.data.path.encode("utf-8")
        obj = self.context.restrictedTraverse(path)
    
        return IRotating(obj).getItems(self.data.limit)

    def title(self):
        """
        """
        return self.data.name
                        
class AddForm(base.AddForm):
    """
    """
    form_fields = form.Fields(IRotatingPortlet)
    label = _(u"Rotating Portlet")
    description = _(u"This portlet displays rotating objects.")

    def create(self, data):
        """
        """
        return Assignment(
            name  = data.get("name", u"Title"),
            path  = data.get('path', u''),
            limit = data.get('limit', 5),
        )

class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(IRotatingPortlet)
    label = _(u"Edit Rotating Portlet")
    description = _(u"This portlet displays rotating objects.")