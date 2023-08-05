# Zope imports
from DateTime import DateTime

# zope imports
from zope.formlib import form
from zope.interface import implements
from zope import schema

# plone imports
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# CMFPlone imports
from Products.CMFPlone import PloneMessageFactory as _

# iqpp.rating imports
from iqpp.plone.rating.interfaces import IPloneRatingConfiglet

class IMostActiveRatedPortlet(IPortletDataProvider):
    """
    """
    count = schema.Int(title=_(u'Number of objects to display'),
                       description=_(u'How many objects to list.'),
                       required=True,
                       default=5)
    
    range = schema.Choice(
         title=_(u"Range"),
         description=_(u"Which time range should be used?"),
         values=(u"daily", u"always"),
         default="daily",
    )
    
class Assignment(base.Assignment):
    """
    """
    implements(IMostActiveRatedPortlet)

    def __init__(self, count=5, range='daily'):
        """
        """
        self.count = count
        self.range = range

    @property
    def title(self):
        """
        """
        if self.range == "always":
            return _(u"Most active rated (always)")            
        else:
            return _(u"Most active rated (daily)")

class Renderer(base.Renderer):
    """
    """
    render = ViewPageTemplateFile('most_active.pt')

    @property
    def available(self):
        """
        """
        # Note that we take the global options here
        utool = getToolByName(self.context, "portal_url")
        portal = utool.getPortalObject()
        
        ro = IPloneRatingConfiglet(portal)
        if not ro.is_enabled:
            return False
        
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("iqpp.rating: details", self.context)
        
    def Title(self):
        """
        """
        if self.data.range == "always":
            return _(u"Most active rated (always)")            
        else:
            return _(u"Most active rated (daily)")
        
    def getMostActiveObjects(self):
        """
        """
        limit = self.data.count
        catalog = getToolByName(self.context, "portal_catalog")

        if self.data.range == "always":
            brains = catalog.searchResults(
                object_provides = "iqpp.rating.interfaces.IRateable",
                sort_on = "amount_of_ratings",
                sort_order = "descending",
            )[:limit]        
        else:
            brains = catalog.searchResults(
                object_provides = "iqpp.rating.interfaces.IRateable",
                last_rating = DateTime().earliestTime(),
                sort_on = "daily_amount_of_ratings",
                sort_order = "descending",
            )[:limit]        
            
        return brains
        
class AddForm(base.AddForm):
    """
    """
    form_fields = form.Fields(IMostActiveRatedPortlet)
    label = _(u"Add Most Active Portlet")
    description = _(u"This portlet displays the objects which are most active rated.")

    def create(self, data):
        """
        """
        return Assignment(
            range=data.get('range', 'daily'), 
            count=data.get('count', 5))

class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(IMostActiveRatedPortlet)
    label = _(u"Edit Most Active Portlet")
    description = _(u"This portlet displays the objects which are most active rated.")
