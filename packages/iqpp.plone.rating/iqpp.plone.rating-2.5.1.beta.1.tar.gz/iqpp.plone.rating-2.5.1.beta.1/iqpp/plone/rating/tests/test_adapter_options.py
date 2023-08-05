# test imports
from base import RatingTestCase

# iqpp.plone.rating imports
from iqpp.plone.rating.interfaces import IRatingOptions

class TestOptions(RatingTestCase):

    def testInit(self):
        """
        """
        d = self.portal.document
        ro = IRatingOptions(d)
        
        self.failUnless(ro.options["is_enabled"] == u"default")
        self.failUnless(ro.options["kind_of_rating_form"] == u"default")
        self.failUnless(ro.options["score_card"] == u"")
                
        self.failUnless(ro.overrides == [])
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOptions))
    return suite
