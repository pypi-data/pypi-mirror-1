# zope imports
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('iqpp.plone.rating')

# plone imports
from plone.app.controlpanel.form import ControlPanelForm
from iqpp.plone.rating.interfaces import IPloneRatingConfiglet

class PloneRatingConfigurationForm(ControlPanelForm):
    """
    """
    form_fields = form.Fields(IPloneRatingConfiglet)

    label = _(u"Rating settings")
    description = _(u"Here you can set global rating options.")
    form_name = _("Rating settings")
