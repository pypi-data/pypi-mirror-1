# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager

class AmountOfRatingsViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('amount_of_ratings.pt')

    def update(self):
        """
        """
        self.amount_of_ratings = self._getAmountOfRatings()

    def _getAmountOfRatings(self):
        """
        """
        rm = IRatingManager(self.context)
        return rm.getAmountOfRatings("plone")