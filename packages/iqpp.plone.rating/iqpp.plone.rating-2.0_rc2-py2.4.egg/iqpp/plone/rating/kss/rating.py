# kss imports
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode, kssaction

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.plone.rating.config import *
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.utils import stringToUnicode
class RatingKSSView(PloneKSSView):
    """
    """
    @kssaction
    def rate(self, form, portlethash):
        """
        """
        rating_id    = stringToUnicode(form.get("rating_id"))
        rating_value = stringToUnicode(form.get("rating_value"))
        ipaddress    = self.request.get("REMOTE_ADDR")        
                        
        if rating_value != "please_rate":        
            mtool = getToolByName(self.context, "portal_membership")
            user = stringToUnicode(mtool.getAuthenticatedMember().getId())
            
            # store rating
            rm = IRatingManager(self.context)
            result = rm.rate(user, rating_id, rating_value, ipaddress)
            self.context.reindexObject()
                        
            message = MESSAGES[result]
            self.getCommandSet('plone').issuePortalMessage(message)
            self.getCommandSet('plone').refreshPortlet(portlethash)
            
            return self.render()
            