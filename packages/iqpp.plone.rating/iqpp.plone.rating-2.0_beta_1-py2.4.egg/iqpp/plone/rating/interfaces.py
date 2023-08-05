# zope imports
from zope import schema
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory
from zope.viewlet.interfaces import IViewletManager
_ = MessageFactory('iqpp.plone.rating')

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingOptions

class IPloneRatingTab(Interface):
    """
    """
    is_enabled = schema.Bool(title=_(u"Enabled"),
         description=_(u"Is rating enabled?"),
         default=False,
    )

class IPloneRatingConfiglet(Interface):
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


class IRatingPortletViewletManager(IViewletManager):
    """
    """
    
# Unfortunately this is not working: IPloneRatingTab will return 
# PloneRatingOptions instead of PloneRatingTab then.
# class IPloneRatingTab(IRatingOptions):
#     """
#     """
    