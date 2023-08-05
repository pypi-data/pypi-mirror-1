# zope imports
from zope.interface import Interface
from zope.interface import implements

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.config import *

class IBestRatedView(Interface):    
    """
    """
    def getRatedObjects():
        """Returns all rated objects, sorted on avarage rating.
        """

    def hideNumberOfRatingsLink():
        """Returns True if the link to number of ratings is to be hidden.
        """

    def getSortOnOptions(self):
        """Returns options for sort on selection.
        """

    def getSortOrderOptions(self):
        """Returns options for sort order selection.
        """
        
class BestRatedView(BrowserView):
    """
    """
    implements(IBestRatedView)

    def getRatedObjects(self):
        """
        """        
        sort_on    = self.request.get("sort_on", "")
        sort_order = self.request.get("sort_order", "")        
        
        query = {
            "object_provides" : "iqpp.plone.rating.interfaces.IRateable",
            "sort_order"      : DEFAULT_SORT_ORDER,
            "sort_on"         : DEFAULT_SORT_ON,
        }
        
        if sort_on == "amount_of_ratings":
            query["sort_on"] = "amount_of_ratings"

        if sort_order == "ascending":
            query["sort_order"] = "ascending"
                        
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(query)

        return brains
        
    def hideNumberOfRatingsLink(self):
        """
        """        
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.checkPermission("iqpp.plone.rating.manage", self.context) is None:
            return True
            
    def getSortOnOptions(self):
        """
        """
        selected_sort_on = self.request.get("sort_on", DEFAULT_SORT_ON)

        result = []
        for option in SORT_ON_OPTIONS:
            result.append({
                "name"     : option["name"],
                "value"    : option["value"],
                "selected" : option["value"] == selected_sort_on,
            })
            
        return result

    def getSortOrderOptions(self):
        """
        """
        selected_sort_order = self.request.get("sort_order", DEFAULT_SORT_ORDER)

        result = []
        for option in SORT_ORDER_OPTIONS:
            result.append({
                "name"     : option["name"],
                "value"    : option["value"],
                "selected" : option["value"] == selected_sort_order,
            })
            
        return result
        
            