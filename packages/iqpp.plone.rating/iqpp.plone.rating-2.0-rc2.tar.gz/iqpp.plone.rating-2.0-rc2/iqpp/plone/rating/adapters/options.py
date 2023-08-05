# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.adapters.options import RatingOptions
from iqpp.plone.rating.controlpanel.rating import IPloneRatingControlPanel

KEY = "iqpp.rating.options"
                
class PloneRatingOptions(RatingOptions):
    """An adapter which provides IRatingOptions for rateable objects.
    """
    def getGlobalOption(self, name):
        """We take the global options out of the configlet.
        """
        utool = getToolByName(self.context, "portal_url")
        portal = utool.getPortalObject()
                
        ro = IPloneRatingControlPanel(portal)
        return getattr(ro, name)