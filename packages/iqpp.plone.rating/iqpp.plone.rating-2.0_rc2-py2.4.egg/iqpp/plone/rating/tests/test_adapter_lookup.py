# Zope imports
from AccessControl import Unauthorized
from datetime import datetime
from datetime import timedelta

# zope imports
from zope.interface import directlyProvides
from zope.component import provideUtility, queryUtility

# test imports
from base import RatingTestCase

# iqpp.rating imports
from iqpp.rating.interfaces import IRatingManager
from iqpp.rating.interfaces import IRatingOptionsSchema
from iqpp.rating.interfaces import IRatingOptions
from iqpp.plone.rating.controlpanel.rating import IPloneRatingControlPanel

class TestAdapterLookup(RatingTestCase):
    """
    """
    def testIRatingManager(self):
        """
        """        
        # As iqpp.plone.rating overrides the rating manager adapter, we expect
        # to get PloneRatingManager here.
        rm = IRatingManager(self.portal.document)
        self.assertEqual(
            str(rm.__class__),
            "<class 'iqpp.plone.rating.adapters.manager.PloneRatingManager'>")

    def testIRatingOptions(self):
        """
        """
        # As iqpp.plone.rating overrides the rating option adapter, we expect
        # to get PloneRatingManager here.
        ro = IRatingOptions(self.portal.document)
        self.assertEqual(
            str(ro.__class__),
            "<class 'iqpp.plone.rating.adapters.options.PloneRatingOptions'>")

    def testIRatingOptionsSchema(self):
        """
        """
        # As iqpp.plone.rating overrides the rating option adapter, we expect
        # to get PloneRatingManager here.
        ro = IRatingOptionsSchema(self.portal.document)
        self.assertEqual(
            str(ro.__class__),
            "<class 'iqpp.rating.adapters.options.RatingOptions'>")

    def testIPloneRatingControlPanel(self):
        """
        """        
        ro = IPloneRatingControlPanel(self.portal)
        self.assertEqual(
            str(ro.__class__),
            "<class 'iqpp.plone.rating.controlpanel.rating.PloneRatingControlPanelAdapter'>")
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapterLookup))        
    return suite
