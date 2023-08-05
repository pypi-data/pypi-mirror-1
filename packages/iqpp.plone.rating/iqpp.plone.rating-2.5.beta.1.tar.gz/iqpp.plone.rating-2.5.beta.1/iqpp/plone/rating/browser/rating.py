# Zope imports
from AccessControl import Unauthorized

# zope imports
from zope.interface import Interface
from zope.interface import implements

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# CMF imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five.browser import BrowserView

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingManager

# iqpp.plone.rating imports
from iqpp.plone.rating.config import MESSAGES
from iqpp.plone.rating.interfaces import IRateable

class IRatingView(Interface):
    """
    """
    def rate():
        """Rates an object.
        """

    def rate_with_stars(self):
        """Rates an object by clicking on a star.
        """

    def isRateable():
        """Returns True if an object is rateable.        
        """
        
class RatingView(BrowserView):
    """
    """
    implements(IRatingView)

    def rate_with_stars(self):
        """
        """
        rating_value = safe_unicode(self.request.get("value",""))
        self._setRate(rating_value)
        
    def rate(self):
        """
        """
        rating_value = safe_unicode(self.request.get("rating_value"))
        self._setRate(rating_value)
        
    def _setRate(self, rating_value):
        """
        """        
        rating_id    = safe_unicode(self.request.get("rating_id", u"plone"))
        ipaddress    = self.request.get("REMOTE_ADDR")
                
        if rating_value != "please_rate":
            mtool = getToolByName(self.context, "portal_membership")
            user = safe_unicode(mtool.getAuthenticatedMember().getId())

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