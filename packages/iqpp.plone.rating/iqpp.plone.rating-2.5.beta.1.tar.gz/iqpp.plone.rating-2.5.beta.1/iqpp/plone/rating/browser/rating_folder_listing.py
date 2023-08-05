# zope imports
from zope.interface import Interface
from zope.interface import implements

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRateable
from iqpp.plone.rating.interfaces import IRatingManager

class IRatingFolderListingView(Interface):    
    """
    """
    
    def getAmountOfRatings():
        """
        """

    def getAverageRating():
        """
        """
        
    def getScores():
        """
        """

    def showRatingForm():
        """
        """
        
class RatingFolderListingView(BrowserView):
    """
    """
    implements(IRatingFolderListingView)

    def getAmountOfRatings(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAmountOfRatings("plone")

    def getAverageRating(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAverageRating("plone")
    
    def getScores(self):
        """
        """
        rm = IRatingManager(self.context)
        rd = rm.getRatingDefinition("plone")

        mtool = getToolByName(self.context, "portal_membership")
        user = mtool.getAuthenticatedMember().getId()
        rating = rm.getRating("plone", user)

        result = []
        for s in rd.scores:
            result.append({
                "id"       : s[0],
                "title"    : s[0],
                "selected" : rating == s[0],
            })
            
        return result
        
    def showRatingForm(self):
        """
        """
        return IRateable.providedBy(self.context)
        