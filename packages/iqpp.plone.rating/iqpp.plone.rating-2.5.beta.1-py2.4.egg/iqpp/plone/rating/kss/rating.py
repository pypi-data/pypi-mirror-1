# kss imports
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode, kssaction

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.config import *
from iqpp.plone.rating.interfaces import IRatingManager

class RatingKSSView(PloneKSSView):
    """
    """
    @kssaction
    def rate(self, form, portlethash):
        """
        """
        rating_value = form.get("rating_value")
        self._setRate(rating_value, portlethash)
        
    @kssaction
    def starRate(self, rating_value, portlethash):
        """
        """                
        self._setRate(rating_value, portlethash)
        
    def _setRate(self, rating_value, portlethash):
        """
        """
        rating_value = safe_unicode(rating_value)
        ipaddress = self.request.get("REMOTE_ADDR")
        
        if rating_value != "please_rate":
            mtool = getToolByName(self.context, "portal_membership")
            user = safe_unicode(mtool.getAuthenticatedMember().getId())
            
            # store rating
            rm = IRatingManager(self.context)
            result = rm.rate(user, u"plone", rating_value, ipaddress)
            self.context.reindexObject()
                        
            message = MESSAGES[result]
            self.getCommandSet('plone').issuePortalMessage(message)
            self.getCommandSet('plone').refreshPortlet(portlethash)
            
            return self.render()
            
