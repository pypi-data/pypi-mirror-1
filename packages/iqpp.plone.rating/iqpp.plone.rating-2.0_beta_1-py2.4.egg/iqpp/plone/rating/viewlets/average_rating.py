# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager

class AverageRatingViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('average_rating.pt')

    def update(self):
        """
        """
        self.average_rating = self._getAverageRating()

    def _getAverageRating(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAverageRating("plone")