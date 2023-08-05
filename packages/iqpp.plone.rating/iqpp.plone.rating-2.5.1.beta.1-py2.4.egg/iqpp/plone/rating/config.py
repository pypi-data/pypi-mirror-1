from zope.i18nmessageid import MessageFactory
_ = MessageFactory("rating")

GLOBALS = globals()
PROJECTNAME = "iqpp.plone.rating"

MESSAGES = {
    "rating-added"       : _(u"Your rating has been added."),
    "rating-changed"     : _(u"Your rating has been changed."),
    "already-rated"      : _(u"You have already rated, please come back later."),
    "rating-deleted"     : _(u"Your rating has been deleted."),
    "rating-not-deleted" : _(u"Your rating cannot been deleted."),
    "options-saved"      : _(u"Your options has been saved"),
}

DEFAULT_SORT_ORDER = "descending"
SORT_ORDER_OPTIONS = [
    {"name"  : _(u"Ascending"),
     "value" : "ascending"},
    {"name"  : _(u"Descending"),
     "value" : "descending"}]
     
DEFAULT_SORT_ON  = "average_rating"
SORT_ON_OPTIONS = [
    {"name"  : _(u"Best Rated"),
     "value" : "average_rating"},
    {"name"  : _(u"Most Rated"),
     "value" : "amount_of_ratings"}]
     
KIND_OF_RATING_FORM_CHOICES = (
    (_(u"Default"),   u'default'),
    (_(u"Stars"),     u'stars'),
    (_(u"Selection"), u'selection'),
)

DEFAULT_CHOICES = (
    (_(u"Default"),  'default'),
    (_(u"Enabled"),  True),
    (_(u"Disabled"), False),
)
     