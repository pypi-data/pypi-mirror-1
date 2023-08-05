# zope imports
from zope.interface import implements

# iqpp imports
from iqpp.plone.rating.interfaces import IRatedEvent

class Rated(object):
    """An event to notify a rating has been made.
    """
    implements(IRatedEvent)
    
    def __init__(self, old_score, score, user, context):
        """
        """
        self.old_score = old_score
        self.score = score
        self.context = context  
        self.user = user