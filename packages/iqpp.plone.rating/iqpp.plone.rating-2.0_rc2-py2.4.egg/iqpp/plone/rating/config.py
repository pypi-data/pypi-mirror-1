GLOBALS = globals()
PROJECTNAME = "iqpp.rating"

MESSAGES = {
    "rating-added"       : "Your rating has been added.",
    "rating-changed"     : "Your rating has been changed.",
    "already-rated"      : "You have already rated, please come back later.",
    "rating-deleted"     : "Your rating has been deleted.",
    "rating-not-deleted" : "Your rating cannot been deleted.",
}

DEFAULT_SORT_ORDER = "descending"
SORT_ORDER_OPTIONS = [
    {"name"  : "Ascending",
     "value" : "ascending"},
    {"name"  : "Descending",
     "value" : "descending"}]
     
DEFAULT_SORT_ON  = "average_rating"
SORT_ON_OPTIONS = [
    {"name"  : "Best Rated",
     "value" : "average_rating"},
    {"name"  : "Most Rated",
     "value" : "amount_of_ratings"}]

