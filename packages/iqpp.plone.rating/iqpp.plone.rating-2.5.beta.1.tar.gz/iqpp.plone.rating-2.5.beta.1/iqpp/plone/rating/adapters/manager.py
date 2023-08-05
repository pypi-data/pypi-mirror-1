# Zope imports
from DateTime import DateTime

# zope imports
from zope.interface import implements
from zope.component import adapts, queryUtility
from zope.app.annotation.interfaces import IAnnotations
from zope.event import notify
from BTrees.OOBTree import OOBTree

# iqpp.plone.rating imports
from iqpp.plone.rating.content.definition import RatingDefinition
from iqpp.plone.rating.content.rating import AnonymousRating
from iqpp.plone.rating.content.rating import Rating
from iqpp.plone.rating.events import Rated
from iqpp.plone.rating.interfaces import IRateable
from iqpp.plone.rating.interfaces import IRatingManager
from iqpp.plone.rating.interfaces import IRatingOptions


KEY1 = "iqpp.plone.rating.members"
KEY2 = "iqpp.plone.rating.anonymous"
KEY3 = "iqpp.plone.rating.daily"

class RatingManager(object):
    """Adapter to manage ratings for arbitrary objects.
    """
    implements(IRatingManager)
    adapts(IRateable)
    
    def __init__(self, context):
        """
        """
        self.context = context    
        annotations = IAnnotations(context)
        
        self.member_ratings = annotations.get(KEY1)
        if self.member_ratings is None:
            self.member_ratings = annotations[KEY1] = OOBTree()

        self.anonymous_ratings = annotations.get(KEY2)
        if self.anonymous_ratings is None:
            self.anonymous_ratings = annotations[KEY2] = OOBTree()

        self.daily_ratings = annotations.get(KEY3)
        if self.daily_ratings is None:
            self.daily_ratings = annotations[KEY3] = {
                "last_rating" : DateTime().earliestTime()-1,
                "amount_of_ratings" : 0,
            }
        
    def deleteRating(self, id, user):
        """
        """
        try:
            del self.member_ratings[id][user]
        except KeyError:
            return False
        
        return True    
        
    def getAmountOfRatings(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        amount_member_ratings = 0
        amount_anonymous_ratings = 0
        
        rating_definition = self.getRatingDefinition(id)
        
        member_ratings = self.member_ratings.get(id)
        if member_ratings is not None:            
            amount_member_ratings = len(member_ratings)
        
        anonymous_ratings = self.anonymous_ratings.get(id)
        if anonymous_ratings is not None:                
            amount_anonymous_ratings = anonymous_ratings.amount_of_ratings

        return amount_member_ratings + amount_anonymous_ratings

    def getAverageRating(self, id=None):
        """
        """
        # TODO: Calculate this after a rate not when the average rating is to
        # be displayed. But then we need additionally we need a mechanism to
        # update average rating for every object after the score card has been 
        # changed.
        
        if id is None:
            id = self.getRatingId()
        
        definition = self.getRatingDefinition(id)
                
        member_total_value  = 0
        member_total_amount = 0

        # Member ratings
        ratings = self.member_ratings.get(id, {}).values()
        for rating in ratings:
            member_total_value  += definition.getNumericalValue(rating.score)
            member_total_amount += 1

        # Anomyous ratings
        anon_total_value  = 0
        anon_total_amount = 0

        ratings = self.anonymous_ratings.get(id)
        if ratings is not None:
            for score in ratings.scores.keys():
                anon_total_value  += definition.getNumericalValue(score) * ratings.scores[score]
                anon_total_amount += ratings.scores[score]
        try:
            average_rating = (member_total_value + anon_total_value) / \
                             (member_total_amount + anon_total_amount)
        except ZeroDivisionError:
            average_rating = 0
            
        return "%.1f" % average_rating

    def getRatingDefinition(self, id=None):
        """Takes the definition out of a coniglet.
        """
        # Todo: This should be a utility.
        
        # Only for Plone's rating card (And not to break other products which
        # use iqpp.plone.rating).
        ro = IRatingOptions(self.context)
        score_card = ro.getEffectiveOption("score_card")
        scores = score_card.split("\n")
    
        if len(scores) == 0:
            return None
        
        score_card = []
        for score in scores:
            id, title, value = score.split(":")
            try:
                value = float(value)
            except ValueError:
                value = 0
            score_card.append((id, title, value))
        
        return RatingDefinition(
            "Plone", 
            score_card, 
            "Scores for Plone content")
            
    def getRatings(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        rating_definition = self.getRatingDefinition(id)
        ratings = list(self.member_ratings.get(id, {}).values())

        if self.anonymous_ratings.get(id) is not None:
            ratings.append(self.anonymous_ratings.get(id))
            
        return ratings
    
    def getRating(self, id=None, user=None):
        """
        """        
        if id is None:
            id = self.getRatingId()
        
        rating_definition = self.getRatingDefinition(id)
        if user is None:
            try:
                return self.anonymous_ratings[id].score
            except KeyError:
                return None
        else:    
            try:
                return self.member_ratings[id][user].score
            except KeyError:
                return None

    def getRatingId(self):
        """
        """
        try:
            return self.context.getRatingId()
        except AttributeError:
            return None
        
    def getScores(self, id=None):
        """
        """
        if id is None:
            id = self.getRatingId()
        
        scores = {}        
        
        member_ratings = self.member_ratings.get(id, {}).values()        
        for rating in member_ratings:
            if scores.has_key(rating.score) == False:
                scores[rating.score] = 0
            scores[rating.score] += 1    

        anonymous_ratings = self.anonymous_ratings.get(id)
        if anonymous_ratings is not None:        
            for score in anonymous_ratings.scores.keys():
                if scores.has_key(score) == False:
                    scores[score] = 0
                scores[score] += anonymous_ratings.scores.get(score)
        
        return scores

    def hasRated(self, id, user):
        """
        """
        if self.getRating(id, user) is not None:
            return True

        return False
        
    def rate(self, user, id, score, ipaddress=None, notify_=True):
        """
        """
        rating_definition = self.getRatingDefinition(id)
        if not rating_definition.isValidScore(score):
            raise ValueError('Invalid rating score %s for %s.' % (score, id))
        
        # Anonymous users: There is only one AnonymousRating object for all 
        # anonymous ratings.
        if user is None:
            if id not in self.anonymous_ratings:
                self.anonymous_ratings[id] = AnonymousRating(id)

            value = rating_definition.getNumericalValue(score)
            rating = self.anonymous_ratings[id]
            old_score = rating.score
            
            # Add Value
            result = rating.addValue(value, score, ipaddress)
            
            if result == True:
                result = "rating-added"
                self._calcDailyRating()
            else:
                result = "already-rated"
                
        # Members: There is one Rating object for every member.
        else:                                
            if id not in self.member_ratings:
                self.member_ratings[id] = OOBTree()
            
            rating = self.member_ratings[id].get(user)
            if rating is None:
                old_score = 0
                result = "rating-added"
                self._calcDailyRating()
            else:
                old_score = rating.score
                result = "rating-changed"
            self.member_ratings[id][user] = Rating(id, score, user)

            # sent event
            if notify_ == True:
                notify(Rated(old_score, score, user, self.context))

        self.context.reindexObject()
        return result
        
    def rateWithConfirmation(self):
        """
        """    
        # not implemented yet
     
    def setRating(self, score, id, user):
        """
        """
        # not implemented yet

    def _calcDailyRating(self):
        """
        """
        last_rating = self.daily_ratings["last_rating"]
        today = DateTime().earliestTime()
        if today - last_rating >= 1:
            self.daily_ratings["last_rating"] = today
            self.daily_ratings["amount_of_ratings"] = 0
            
        self.daily_ratings["amount_of_ratings"] += 1