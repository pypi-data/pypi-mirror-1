# zope imports
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.formlib import form
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('iqpp.plone.rating')

# CMF imports
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot

# plone imports
from plone.app.controlpanel.form import ControlPanelForm

class IPloneRatingControlPanel(Interface):
    """
    """
    is_enabled = schema.Bool(title=_(u"Enabled"),
         description=_(u"Is rating enabled?"),
         default=True,
    )
    
    score_card = schema.Text(
        title=_(u'The Score Card'),
        description=_(u"The score card. One title:value pair per line."),
        default=u"""excellent:5\ngood:4\naverage:3\nbelow average:2\nbad:1""",
        required=True)

class PloneRatingControlPanelForm(ControlPanelForm):
    """
    """
    form_fields = form.Fields(IPloneRatingControlPanel)

    label = _(u"Rating settings")
    description = _(u"Here you can set global rating options.")
    form_name = _("Rating settings")
    
class PloneRatingControlPanelAdapter(SchemaAdapterBase):
    """
    """    
    implements(IPloneRatingControlPanel)    
    adapts(IPloneSiteRoot)
    
    def __init__(self, context):
        """
        """
        super(PloneRatingControlPanelAdapter, self).__init__(context)
        
    is_enabled = ProxyFieldProperty(IPloneRatingControlPanel['is_enabled'])
    score_card = ProxyFieldProperty(IPloneRatingControlPanel['score_card'])