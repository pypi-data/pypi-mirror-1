# Zope imports
from AccessControl import Unauthorized

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility

# test imports
from base import RatingTestCase

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRateable
from iqpp.plone.rating.interfaces import IRatingManager
from iqpp.plone.rating.interfaces import IRatingDefinition    
from iqpp.plone.rating.content.definition import RatingDefinition

class TestRating(RatingTestCase):

    def testRate(self):
        rm = IRatingManager(self.portal.document)
        
        rm.rate(id=u"score", score=u"bad", user=u"john")
        rm.rate(id=u"score", score=u"below average", user=u"jane")
        rm.rate(id=u"score", score=u"average", user=u"ben")
                        
        rating = rm.getRating(id="score", user="john")
        self.assertEqual(rating, "bad")

        rating = rm.getRating(id="score", user="jane")
        self.assertEqual(rating, "below average")

        rating = rm.getRating(id="score", user="ben")
        self.assertEqual(rating, "average")

        ratings = rm.getRatings(id="score")
        self.assertEqual(len(ratings), 3)

        ratings = rm.getAmountOfRatings(id="score")
        self.assertEqual(ratings, 3)

        average = rm.getAverageRating(id="score")
        self.assertEqual(average, "2.0")

    def testNoRatings(self):
        rm = IRatingManager(self.portal.document)
        average = rm.getAverageRating(id="score")
        self.assertEqual(average, "0.0")
        
    def testWrongValue(self):
        rm = IRatingManager(self.portal.document)
        self.assertRaises(ValueError, rm.rate, id="score", score="42", user="john")

    def testWrongDefinition(self):
        rm = IRatingManager(self.portal.document)
        self.assertRaises(ValueError, rm.rate, id="wrong", score="1", user="john")

    def testChangeRating(self):
        rm = IRatingManager(self.portal.document)

        rm.rate(id=u"score", score=u"bad", user=u"john")
        rating = rm.getRating(id=u"score", user=u"john")
        self.assertEqual(rating, "bad")
        
        rm.rate(id=u"score", score=u"below average", user=u"john")
        rating = rm.getRating(id=u"score", user=u"john")        
        self.assertEqual(rating, "below average")

class TestRatingAsAnonymous(RatingTestCase):

    def testRate_1(self):
        """
        """
        rm = IRatingManager(self.portal.document)
        self.logout()

        rm.rate(id=u"score", user=None, score=u"bad", ipaddress=u"127.0.0.1")
        rm.rate(id=u"score", user=None, score=u"below average", ipaddress=u"127.0.0.2")
        rm.rate(id=u"score", user=None, score=u"average", ipaddress=u"127.0.0.3")

        self.login("test_user_1_")

        ratings = rm.getRatings(id="score")
        self.assertEqual(len(ratings), 1)

        ratings = rm.getAmountOfRatings(id="score")
        self.assertEqual(ratings, 3)
        
        average = rm.getAverageRating(id="score")
        self.assertEqual(average, "2.0")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRating))        
    suite.addTest(makeSuite(TestRatingAsAnonymous))
    return suite
