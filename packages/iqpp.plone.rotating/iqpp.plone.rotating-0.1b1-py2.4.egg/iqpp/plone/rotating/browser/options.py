# zope imports
from zope.formlib import form

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five.formlib import formbase
from Products.Five.browser import pagetemplatefile

# iqpp.rating imports
from iqpp.plone.rotating.config import MESSAGES
from iqpp.plone.rotating.interfaces import IRotatingOptions

class OptionsForm(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(IRotatingOptions)
    template = pagetemplatefile.ZopeTwoPageTemplateFile("options.pt")
    
    @form.action("add")
    def action_add(self, action, data):
        """
        """
        options = IRotatingOptions(self.context)
        options.setOptions(data)
        
        # TODO: for any reason addPortalMessage is not working (means the
        # message is not displayed.)
        ptool = getToolByName(self.context, "plone_utils")
        ptool.addPortalMessage(MESSAGES["options-saved"])
                
        url = self.context.absolute_url() + "/rotating-options"
        self.request.response.redirect(url)