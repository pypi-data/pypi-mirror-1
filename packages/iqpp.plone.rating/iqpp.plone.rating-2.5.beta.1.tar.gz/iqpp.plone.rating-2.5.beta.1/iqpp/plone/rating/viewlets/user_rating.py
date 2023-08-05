# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingManager

class UserRatingViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('user_rating.pt')

    def update(self):
        """
        """
        self.user_rating  = self._getUserRating()
        self.available    = self._available()

    def _available(self):
        """
        """
        # if the user is not authenticated, we can't find out his rating.
        # hence we don't display this section at all.
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.isAnonymousUser() == True:
            return False
        else:
            return True
        
    def _getUserRating(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        user = mtool.getAuthenticatedMember().getId()
        
        rm = IRatingManager(self.context)
        rd = rm.getRatingDefinition(u"plone")
        user_rating = rm.getRating(u"plone", user)
        
        if user_rating is None:
            return {
                "rated" : False,
                "title" : "",
                "value" : "",
            }        

        rd = rm.getRatingDefinition(u"plone")            
        info = rd.getInfo(user_rating)
        return {
            "rated" : True,
            "title" : info["title"],
            "value" : info["value"],
        }