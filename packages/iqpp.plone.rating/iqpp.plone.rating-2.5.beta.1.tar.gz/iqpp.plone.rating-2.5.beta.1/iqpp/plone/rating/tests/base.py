# zope imports
from transaction import commit
from zope.interface import directlyProvides

# Testing imports
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from AccessControl.SecurityManagement import newSecurityManager

# Five imports
from Products.Five import zcml

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.rating imports
import iqpp.plone.rating
from iqpp.plone.rating.interfaces import IRateable
from iqpp.plone.rating.tests import utils

PRODUCTS = []
PloneTestCase.setupPloneSite(products=PRODUCTS)

class RatingLayer(PloneSite):

    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        portal = app.plone

        zcml.load_config('configure.zcml', iqpp.plone.rating)
        
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-iqpp.plone.rating:iqpp.plone.rating')
        
        # login as admin (copied from `loginAsPortalOwner`)
        uf = app.acl_users
        user = uf.getUserById(PloneTestCase.portal_owner).__of__(uf)
        newSecurityManager(None, user)

        commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        pass


class RatingMixin:

    def afterSetUp(self):
        """
        """
        self.setRoles(['Manager'])

        # Create default score card
        utils.createDefinition()

        # A rateable document for all tests to play with
        self.portal.invokeFactory("Document", "document")
        directlyProvides(self.portal.document, IRateable)
        
class RatingTestCase(RatingMixin, PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'iqpp.plone.rating' product.
    """
    layer = RatingLayer

class RatingFunctionalTestCase(RatingMixin, PloneTestCase.FunctionalTestCase):
    """Base class for functional integration tests for the 'iqpp.plone.rating' product.
    """
    layer = RatingLayer
