# Zope imports
from Acquisition import aq_inner

# zope imports
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

# plone imports
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# CMFPlone imports
from Products.CMFPlone import PloneMessageFactory as _

# EasyShop imports
from iqpp.rating.interfaces import IRateable
from iqpp.rating.interfaces import IRatingOptions

class IRatingPortlet(IPortletDataProvider):
    """
    """

class Assignment(base.Assignment):
    """
    """
    implements(IRatingPortlet)

    @property
    def title(self):
        """
        """
        return _(u"Rating")

class Renderer(base.Renderer):
    """
    """
    render = ViewPageTemplateFile('rating.pt')

    @property
    def available(self):
        """
        """
        if not IRateable.providedBy(self.context):
            return False
            
        ro = IRatingOptions(self.context)
        if not ro.getEffectiveOption("is_enabled"):
            return False
            
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.checkPermission("iqpp.rating: rate", self.context) or\
           mtool.checkPermission("iqpp.rating: details", self.context):
            return True
        else:
            return False
        
    def showRatingForm(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("iqpp.rating: rate", self.context)
        
    def showFooter(self):
        """
        """ 
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("iqpp.rating: details", self.context)

class AddForm(base.NullAddForm):
    """
    """
    form_fields = form.Fields(IRatingPortlet)
    label = _(u"Add rating portlet")
    description = _(u"This portlet displays ratings.")

    def create(self):
        """
        """
        return Assignment()
