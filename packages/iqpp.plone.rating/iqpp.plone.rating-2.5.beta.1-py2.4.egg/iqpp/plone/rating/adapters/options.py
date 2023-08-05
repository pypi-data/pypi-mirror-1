# zope imports
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

# CMFCore imports
from Products.CMFCore.utils import getToolByName

KEY = "iqpp.plone.rating.options"
                
# iqpp.plone.rating imports
from iqpp.plone.rating.controlpanel.rating import IPloneRatingControlPanel
from iqpp.plone.rating.interfaces import IRatingOptions
from iqpp.plone.rating.interfaces import IRateable

KEY = "iqpp.plone.rating.options"

class RatingOptions(object):
    """An adapter which provides IRatingOptions for ratable objects.
    """
    adapts(IRateable)
    implements(IRatingOptions)
        
    def __init__(self, context):
        """
        """
        self.context = context

        annotations = IAnnotations(context)
        options = annotations.get(KEY)

        if options is None:
            options = annotations[KEY] = {
                'options'   : PersistentDict(),
                'overrides' : PersistentList(),
            }
            options["options"]["is_enabled"] = \
                IRatingOptions.get("is_enabled").default

            options["options"]["kind_of_rating_form"] = \
                IRatingOptions.get("kind_of_rating_form").default

            options["options"]["score_card"] =\
                IRatingOptions.get("score_card").default


        self.options   = options['options']
        self.overrides = options['overrides']

    def _named_get(self, name):
        """Returns the local option with given name.
        """
        return self.options.get(name, None)
            
    def _named_set(self, name, value):
        """Sets the local option for the given name.
        """
        if name not in self.overrides:
            self.overrides.append(name)
        self.options[name] = value

    def getEffectiveOption(self, name):
        """
        """
        if name in self.overrides:
            return getattr(self, name)
        else:
            return self.getGlobalOption(name)

    def getGlobalOption(self, name):
        """We take the global options out of the control panel.
        """
        utool = getToolByName(self.context, "portal_url")
        portal = utool.getPortalObject()
                
        ro = IPloneRatingControlPanel(portal)
        return getattr(ro, name)

    def _setOverride(self, name):
        """
        """
        if name not in self.overrides:
            self.overrides.append(name)
        
    def _removeOverride(self, name):
        """
        """
        if name in self.overrides:
            self.overrides.remove(name)
        
    @apply
    def is_enabled():
        def get(self):
            return self.options.get("is_enabled")
        def set(self, value):
            if value == "default":
                self._removeOverride("is_enabled")
            else:
                self._setOverride("is_enabled")
            self.options["is_enabled"] = value
        return property(get, set)

    @apply
    def kind_of_rating_form():
        def get(self):
            return self.options.get("kind_of_rating_form")
        def set(self, value):
            if value == "default":
                self._removeOverride("kind_of_rating_form")
            else:
                self._setOverride("kind_of_rating_form")
            self.options["kind_of_rating_form"] = value
        return property(get, set)

    @apply
    def score_card():
        def get(self):
            return self._named_get('score_card')
        def set(self, value):
            # TODO: Be more concise here (if value == \s*)
            if value is None:
                self._removeOverride("score_card")
            else:
                self._setOverride("score_card")
            self.options["score_card"] = value
        return property(get, set)    
