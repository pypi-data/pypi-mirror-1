# zope imports
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('rating')

# Five imports
from Products.Five.formlib import formbase
from Products.Five.browser import pagetemplatefile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.config import MESSAGES
from iqpp.plone.rating.interfaces import IRatingOptions

class RatingOptionsTab(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(IRatingOptions)
    template = pagetemplatefile.ZopeTwoPageTemplateFile("options_tab.pt")
    
    @form.action("add")
    def action_add(self, action, data):
        """
        """
        ro = IRatingOptions(self.context)

        for field in self.form_fields:
            # Set fields
            name = field.__name__
            if name in data.keys():
                setattr(ro, name, data[name])

        # TODO: for any reason addPortalMessage is not working (means the
        # message is not displayed.)
        ptool = getToolByName(self.context, "plone_utils")
        ptool.addPortalMessage(MESSAGES["options-saved"])
                
        url = self.context.absolute_url() + "/rating-options"
        self.request.response.redirect(url)