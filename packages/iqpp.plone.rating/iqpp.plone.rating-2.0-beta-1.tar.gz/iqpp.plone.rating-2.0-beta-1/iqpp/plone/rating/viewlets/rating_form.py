# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager

class RatingFormViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('rating_form.pt')

    def update(self):
        """
        """
        self.scores = self._getScores()
        self.has_rate_permission = self._hasRatePermission()
        
    def _getScores(self):
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

    def _hasRatePermission(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("iqpp.rating: rate", self.context)