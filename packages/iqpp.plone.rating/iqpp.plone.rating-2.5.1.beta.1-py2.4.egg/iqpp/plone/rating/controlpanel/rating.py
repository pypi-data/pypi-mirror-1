# zope imports
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.formlib import form
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('rating')

# CMF imports
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot

# plone imports
from plone.app.controlpanel.form import ControlPanelForm

# iqpp.plone.rating imports
from iqpp.plone.rating.config import KIND_OF_RATING_FORM_CHOICES

class IPloneRatingControlPanel(Interface):
    """
    """
    is_enabled = schema.Bool(title=_(u"Enabled"),
         description=_(u"Is rating enabled?"),
         default=True,
    )
    
    kind_of_rating_form = schema.Choice(
        title=_(u'Kind of rating form'),
        description=_(u"Select the kind of rating the rating form."),
        vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
            KIND_OF_RATING_FORM_CHOICES[1:]),
        default="stars",
        required=True)

    score_card = schema.Text(
        title=_(u'The Score Card'),
        description=_(u"The score card. One id:title:value triple per line."),
        default=u"excellent:Excellent:5\ngood:Good:4\naverage:Average:3\nbelow average:Below Average:2\nbad:Bad:1",
        required=True)

class PloneRatingControlPanelForm(ControlPanelForm):
    """
    """
    form_fields = form.Fields(IPloneRatingControlPanel)

    label = _(u"Rating settings")
    description = _(u"Here you can set global rating options.")
    form_name = _(u"Rating settings")
    
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
    kind_of_rating_form = ProxyFieldProperty(IPloneRatingControlPanel['kind_of_rating_form'])
    score_card = ProxyFieldProperty(IPloneRatingControlPanel['score_card'])