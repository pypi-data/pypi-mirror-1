# Zope imports
from zope.interface import Interface
from zope.interface import implements

# CMF imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five.browser import BrowserView

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.utils import stringToUnicode

# iqpp.plone.rating imports
from iqpp.plone.rating.config import MESSAGES
from iqpp.rating.interfaces import IRateable

class IRatingView(Interface):
    """
    """
    def rate():
        """Rates an object.
        """

    def isRateable():
        """Returns True if an object is rateable.        
        """
        
class RatingView(BrowserView):
    """
    """
    implements(IRatingView)

    def rate(self):
        """
        """                
        rating_id    = stringToUnicode(self.request.get("rating_id"))
        rating_value = stringToUnicode(self.request.get("rating_value"))
        ipaddress    = self.request.get("REMOTE_ADDR")        

        if rating_value != "please_rate":
            mtool = getToolByName(self.context, "portal_membership")
            user = stringToUnicode(mtool.getAuthenticatedMember().getId())

            # store rating
            rm = IRatingManager(self.context)
            result = rm.rate(user, rating_id, rating_value, ipaddress)
                                    
            utils = getToolByName(self.context, "plone_utils")
            utils.addPortalMessage(MESSAGES[result])

        url = self.request.get("HTTP_REFERER")

        if url is None:
            url = "%s/view" % self.context.absolute_url()
            
        self.request.response.redirect(url)
        
    def isRateable(self):
        """
        """
        return IRateable.providedBy(self.context)