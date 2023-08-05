# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingManager

class RatingStarsViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('rating_stars.pt')

    def update(self):
        """
        """
        self.average_width = self._getAverageWidth()         
        self.average_rating = self._getAverageRating()
        self.has_rate_permission = self._hasRatePermission()        
        self.scores = self._getScores()
        self.total_width = self._getTotalWidth()

    def _hasRatePermission(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.checkPermission("iqpp.plone.rating: rate", self.context) == True:
            return True
        else:
            return False
            
    def _getAverageWidth(self):
        """
        """
        rm = IRatingManager(self.context)
        rating_definition = rm.getRatingDefinition("plone")        
        average_rating = float(rm.getAverageRating("plone"))        

        # TODO: Find out the real max as score cards don't have the max values
        # in ord 0.        
        # TODO: Need some error handling here
        
        max_score = float(rating_definition.scores[0][2])
        return "width:%s%%" % (average_rating / max_score * 100)
                
    def _getAverageRating(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAverageRating("plone")
                        
    def _getScores(self):
        """
        """    
        rm = IRatingManager(self.context)
        rd = rm.getRatingDefinition("plone")

        mtool = getToolByName(self.context, "portal_membership")
        user = mtool.getAuthenticatedMember().getId()
        rating = rm.getRating("plone", user)

        result = []
        step_width = 100 / len(rd.scores)
        for index, score in enumerate(rd.scores):
            width  = 100 - (step_width * index)
            result.append({
                "id"       : score[0],
                "title"    : score[1],
                "style"    : "z-index:%s; width:%s%%" % (index+2, width)
            })

        result.reverse()
        return result
        
    def _getTotalWidth(self):
        """
        """
        rm = IRatingManager(self.context)
        rd = rm.getRatingDefinition("plone")        
        return "width:%spx" % (len(rd.scores) * 25)
        return "width:%spx" % (len(rd.scores) * 10)