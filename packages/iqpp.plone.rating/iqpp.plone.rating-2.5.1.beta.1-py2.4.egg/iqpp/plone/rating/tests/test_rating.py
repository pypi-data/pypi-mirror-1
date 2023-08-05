# python imports
from pytz import UTC

# Zope imports
from AccessControl import Unauthorized
from datetime import datetime
from datetime import timedelta

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility, queryUtility

# test imports
from base import RatingTestCase

# iqpp.plone.rating imports
from iqpp.plone.rating.content.rating import Rating    
from iqpp.plone.rating.content.rating import AnonymousRating    

class TestRatingDefinition(RatingTestCase):

    def testRating(self):
        rating = Rating(id=u"score", score=u"1", user=u"john")
        
        self.assertEqual(rating.id, u"score")
        self.assertEqual(rating.user, u"john")
        self.assertEqual(rating.score, u"1")        

class TestRatingDefinitionAnonymousRating(RatingTestCase):

    def afterSetUp(self):
        self.rating = AnonymousRating(id=u"score")

    def testInitialization(self):
        self.assertEqual(self.rating.id, u"score")
        self.assertEqual(self.rating.user, u"anonymous")
        self.assertEqual(self.rating.average_rating, 0.0)        
        self.assertEqual(self.rating.amount_of_ratings, 0)
        self.assertEqual(list(self.rating.ipaddresses.keys()), [])
        
    def testAddValue(self):
        result = self.rating.addValue(2, u"2", u"127.0.0.1")
        self.assertEqual(result, True)
        self.assertEqual(self.rating.id, u"score")
        self.assertEqual(self.rating.user, u"anonymous")
        self.assertEqual(list(self.rating.scores.keys()), ["2"])
        self.assertEqual(self.rating.amount_of_ratings, 1)  
        self.assertEqual(list(self.rating.ipaddresses.keys()), [u"127.0.0.1"])

        result = self.rating.addValue(4, u"4", u"127.0.0.2")
        self.assertEqual(result, True)
        self.assertEqual(self.rating.id, u"score")
        self.assertEqual(self.rating.user, u"anonymous")
        self.assertEqual(list(self.rating.scores.keys()), [u"2", u"4"])
        self.assertEqual(self.rating.amount_of_ratings, 2)  
        self.assertEqual(list(self.rating.ipaddresses.keys()), [u"127.0.0.1", u"127.0.0.2"])

        result = self.rating.addValue(4, u"4", u"127.0.0.2")
        self.assertEqual(result, False)

    def testAddValueSameIPAfterOneDay(self):
        result = self.rating.addValue(2, "2", "127.0.0.1")
        self.assertEqual(result, True)
        self.assertEqual(self.rating.id, "score")
        self.assertEqual(self.rating.user, "anonymous")
        self.assertEqual(list(self.rating.scores.keys()), ["2"])
        self.assertEqual(self.rating.amount_of_ratings, 1)
        self.assertEqual(list(self.rating.ipaddresses.keys()), ["127.0.0.1"])
        
        self.rating.ipaddresses["127.0.0.1"] = datetime.now(UTC) - timedelta(1)
        
        result = self.rating.addValue(4, "4", "127.0.0.1")
        self.assertEqual(result, True)
        self.assertEqual(self.rating.id, "score")
        self.assertEqual(self.rating.user, "anonymous")
        self.assertEqual(list(self.rating.scores.keys()), ["2", "4"])
        self.assertEqual(self.rating.amount_of_ratings, 2)  
        self.assertEqual(list(self.rating.ipaddresses.keys()), ["127.0.0.1"])
                                                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRatingDefinition))        
    suite.addTest(makeSuite(TestRatingDefinitionAnonymousRating))
    return suite
