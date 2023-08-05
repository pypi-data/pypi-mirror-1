# zope imports
from zope.formlib import form

# Five imports
from Products.Five.formlib import formbase
from Products.Five.browser import pagetemplatefile

# iqpp.rating imports
from iqpp.plone.rating.interfaces import IPloneRatingTab

class RatingOptionsTab(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(IPloneRatingTab)
    template = pagetemplatefile.ZopeTwoPageTemplateFile("options.pt")
    
    @form.action("add")
    def action_add(self, action, data):
        """
        """
        ro = IPloneRatingTab(self.context)
        ro.is_enabled = data["is_enabled"]
        
        if self.request.get("is_active", "") == "" and\
           "is_enabled" in ro.overrides:
                ro.overrides.remove("is_enabled")
            
    def isChecked(self):
        """
        """
        ro = IPloneRatingTab(self.context)
        return "is_enabled" in ro.overrides