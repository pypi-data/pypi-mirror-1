# Zope imports
from AccessControl import Unauthorized

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility, queryUtility

# test imports
from base import RatingTestCase

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingDefinition    
from iqpp.plone.rating.content.definition import RatingDefinition

class TestRatingDefinition(RatingTestCase):

    def testQueryDefinition(self):
        definition = queryUtility(IRatingDefinition, "score")
        sc = [("1", "One", 1.0), ("2", "Two", 2.0), ("3", "Three", 3.0), ("4", "Four", 4.0),  ("5", "Five", 5.0),  ("6", "Six", 6.0)]        
                
        self.assertEqual(definition.scores, sc)
        self.assertEqual(definition.title, "Score")
        self.assertEqual(definition.description, "The Score for a Paper")

    def testValidScore(self):
        """
        """
        definition = queryUtility(IRatingDefinition, "score")        
        self.assertEqual(definition.isValidScore("3"), True)
        self.assertEqual(definition.isValidScore("42"), False)

    def testGetNumericalValue(self):
        """
        """
        definition = queryUtility(IRatingDefinition, "score")
        self.assertEqual(definition.getNumericalValue("3"), 3.0)

    def testGetTitle(self):
        """
        """
        definition = queryUtility(IRatingDefinition, "score")        
        self.assertEqual(definition.getTitle("3"), "Three")

    def testGetInfo(self):
        """
        """
        definition = queryUtility(IRatingDefinition, "score")
        info = definition.getInfo("3")
        self.assertEqual(info["title"], "Three")
        self.assertEqual(info["value"], 3.0)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRatingDefinition))
    return suite
