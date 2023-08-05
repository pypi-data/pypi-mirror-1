# zope imports
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('iqpp.plone.rating')

# Five imports
from Products.Five.formlib import formbase
from Products.Five.browser import pagetemplatefile

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptionsSchema

class RatingOptionsTab(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(IRatingOptionsSchema)
    template = pagetemplatefile.ZopeTwoPageTemplateFile("options_tab.pt")
    
    @form.action("add")
    def action_add(self, action, data):
        """
        """
        ro = IRatingOptionsSchema(self.context)

        for field in self.form_fields:
            # Set fields
            name = field.__name__
            if name in data.keys():
                setattr(ro, name, data[name])
            
            # Set override
            is_active_name = "is_active_form.%s" % name
            if self.request.get(is_active_name, "") == "" and\
               name in ro.overrides:
                    ro.overrides.remove(name)

        self.request.response.redirect(self.context.absolute_url())
        
        
    def isChecked(self, field_name):
        """
        """
        field_name = field_name.replace("form.", "")
        ro = IRatingOptionsSchema(self.context)
        return field_name in ro.overrides