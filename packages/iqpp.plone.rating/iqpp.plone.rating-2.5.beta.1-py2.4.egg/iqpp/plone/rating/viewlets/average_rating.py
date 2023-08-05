# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingManager

class AverageRatingViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('average_rating.pt')

    def update(self):
        """
        """
        self.average_rating    = self._getAverageRating()
        self.amount_of_ratings = self._getAmountOfRatings()
        self.available         = self._showAverageRating()

    def _getAverageRating(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAverageRating("plone")
        
    def _getAmountOfRatings(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAmountOfRatings("plone")
        
    def _showAverageRating(self):
        """
        """
        rm = IRatingManager(self.context)
        if rm.getAmountOfRatings("plone") == 0:
            return False
        else:
            return True        