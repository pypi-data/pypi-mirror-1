# zope imports
from zope.interface import implements
from zope.component import adapts

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.adapters.rating import RatingManager
from iqpp.rating.content.definition import RatingDefinition
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingManager

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IPloneRatingConfiglet

class PloneRatingManager(RatingManager):
    """
    """
    implements(IRatingManager)
    adapts(IRateable)
    
    def getRatingDefinition(self, id="plone"):
        """Takes the definition out of a coniglet.
        """
        # Only for Plone's rating card to not break iqpp.rating
        if id != "plone":
            return super(PloneRatingManager, self).getRatingDefinition(id)
        else:
            # TODO: This has to be done nicer (check utility)    
            utool = getToolByName(self.context, "portal_url")
            portal = utool.getPortalObject()
            ro = IPloneRatingConfiglet(portal)
        
            scores = ro.score_card
            scores = scores.split("\n")
        
            if len(scores) == 0:
                return None
            
            score_card = []
            for score in scores:
                name, value = score.split(":")
                try:
                    value = float(value)
                except ValueError:
                    value = 0
                score_card.append((name, value))
            
            return RatingDefinition(
                "Plone", 
                score_card, 
                "Scores for Plone content")

        