# zope imports
from zope.interface import Interface
from zope.interface import implements

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager

class IObjectRatingsView(Interface):
    """
    """
    def displayOptions():
        """Returns True if the user has the permission to see the options.
        """
            
    def getRatings():
        """Returns all ratings for context.
        """

class ObjectRatingsView(BrowserView):
    """
    """
    implements(IObjectRatingsView)

    def displayOptions(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("iqpp.rating: manage",
                                      self.context)
        
    def getRatings(self):
        """
        """        
        ttool = getToolByName(self.context, 'translation_service')
        
        result = []
        rm = IRatingManager(self.context)
        for rating in rm.getRatings("plone"):
            
            if rating.user == "anonymous":
                score = rating.average_rating
            else:
                rm = IRatingManager(self.context)
                definition = rm.getRatingDefinition("plone")
                
                value = definition.getNumericalValue(rating.score)
                score = "%s (%s)" % (rating.score, value)
                
            result.append({
                "user": rating.user,
                "fullname" : self._getFullnameByMemberId(rating.user),
                "score" : score,
                "timestamp" : ttool.ulocalized_time(
                    rating.timestamp.isoformat(), True),
            })
            
        return result

    def _getFullnameByMemberId(self, id):
        """
        """     
        mtool = getToolByName(self.context, "portal_membership")
        creator = self.context.Creator()
        mi = mtool.getMemberInfo(id);
        if mi and mi['fullname']:
            return mi['fullname']

        return id