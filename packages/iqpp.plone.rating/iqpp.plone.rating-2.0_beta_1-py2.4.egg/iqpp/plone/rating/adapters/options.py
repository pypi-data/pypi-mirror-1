# zope imports
from zope.schema.fieldproperty import FieldProperty

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.rating imports
from iqpp.rating.adapters.options import RatingOptions
from iqpp.plone.rating.interfaces import IPloneRatingConfiglet

KEY = "iqpp.rating.options"
                
class PloneRatingOptions(RatingOptions):
    """An adapter which provides IRatingOptions for rateable objects.
    
    This adapter is responsible to return the individual effective option for
    an ratable object. This could be local ones (stored on the object itself) 
    or global ones (stored in the configlet).
    
    The main work is done in the base adapter within iqpp.rating. See there for
    more.
    """
    def getGlobalOption(self, name):
        """We take the global options out of the configlet, in contrary to 
        RatingOptions, which takes options out on of class. See there for 
        more.
        """
        utool = getToolByName(self.context, "portal_url")
        portal = utool.getPortalObject()
                
        ro = IPloneRatingConfiglet(portal)
        return getattr(ro, name)
        
class PloneContextRatingOptions(RatingOptions):
    """An adapter which provides IRatingOptions for rateable objects.    
    
    This one is used to get and set the options on context. This could be 
    the rateable object itself or the configlet (which means the context 
    is the Plone site.)
    """    
    def __init__(self, context):
        """
        """
        super(PloneContextRatingOptions, self).__init__(context)
        self.options.score_card = IPloneRatingConfiglet["score_card"].default
            
    def getGlobalOption(self, name):
        """We just return the local option.
        """
        return getattr(self.options, name)

    def getLocalOption(self, name):
        """We just return the local option.
        """
        return getattr(self.options, name)