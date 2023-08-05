# python imports
from pytz import UTC
from datetime import datetime
from datetime import timedelta

# zope imports
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# Zope imports
from persistent import Persistent
from BTrees.OOBTree import OOBTree

# rating
from iqpp.plone.rating.interfaces import IRating
from iqpp.plone.rating.interfaces import IAnonymousRating

class Rating(Persistent):
    """
    """    
    implements(IRating)

    id = FieldProperty(IRating['id'])
    score = FieldProperty(IRating['score'])
    user = FieldProperty(IRating['user'])
    timestamp = FieldProperty(IRating['timestamp'])

    def __init__(self, id, score, user):
        """
        """
        self.id = id
        self.score = score
        self.user = user
        self.timestamp = datetime.now(UTC)
        
class AnonymousRating(Rating):
    """
    """
    implements(IAnonymousRating)

    amount_of_ratings = FieldProperty(IAnonymousRating['amount_of_ratings'])
    average_rating = FieldProperty(IAnonymousRating['average_rating'])    
    
    def __init__(self, id):
        """
        """
        super(AnonymousRating, self).__init__(id, u"0", u"anonymous")
        self.amount_of_ratings = 0
        self.ipaddresses = OOBTree()
        self.scores = OOBTree()

    def hasRated(self, ipaddress):
        """
        """
        one_day = timedelta(1)
        if ipaddress in self.ipaddresses and\
           (datetime.now(UTC) - self.ipaddresses.get(ipaddress)) < one_day:
           return True
        
        return False
        
    def addValue(self, value, score, ipaddress):
        """
        """
        # If given ipaddress has already rated within a particular time range
        # it isn't allowed to rate again.
        if self.hasRated(ipaddress):
            return False
            
        if self.scores.has_key(score) == False:
            self.scores[score] = 0
        self.scores[score] += 1
        
        # Old approach to calculate the average rating. (Don't consider value changings.)
        # self.average_rating = ((self.average_rating * self.amount_of_ratings) + value) / (self.amount_of_ratings + 1)
        
        self.amount_of_ratings += 1
        self.ipaddresses[ipaddress] = datetime.now(UTC)
        return True