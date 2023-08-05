# zope imports
from zope.interface import implements
from zope.component import adapts

# iqpp.rating imports
from iqpp.rating.adapters.rating import RatingManager
from iqpp.rating.content.definition import RatingDefinition
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingManager

# iqpp.plone.rating imports
from iqpp.rating.interfaces import IRatingOptions

class PloneRatingManager(RatingManager):
    """
    """
    implements(IRatingManager)
    adapts(IRateable)
    
    # TODO: Move this to iqpp.rating
    def getRatingDefinition(self, id="plone"):
        """Takes the definition out of a coniglet.
        """
        # Only for Plone's rating card (And not to break other products which
        # use iqpp.rating).
        if id != "plone":
            return super(PloneRatingManager, self).getRatingDefinition(id)
        else:
            ro = IRatingOptions(self.context)
            score_card = ro.getEffectiveOption("score_card")
            scores = score_card.split("\n")
        
            if len(scores) == 0:
                return None
            
            score_card = []
            for score in scores:
                id, title, value = score.split(":")
                try:
                    value = float(value)
                except ValueError:
                    value = 0
                score_card.append((id, title, value))
            
            return RatingDefinition(
                "Plone", 
                score_card, 
                "Scores for Plone content")