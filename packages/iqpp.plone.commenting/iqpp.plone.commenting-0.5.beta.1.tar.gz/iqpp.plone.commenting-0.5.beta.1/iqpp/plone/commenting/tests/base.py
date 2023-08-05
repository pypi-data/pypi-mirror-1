from transaction import commit
from zope.interface import directlyProvides
from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.Five.testbrowser import Browser as BaseBrowser
from Products.Five import zcml

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
import iqpp.plone.commenting
from iqpp.plone.commenting import catalog
from iqpp.plone.commenting.interfaces import ICommentable

PRODUCTS = []
PloneTestCase.setupPloneSite(products=PRODUCTS)

class Browser(BaseBrowser):

    def addAuthorizationHeader(self, user=PloneTestCase.default_user, password=PloneTestCase.default_password):
        """ add an authorization header using the given or default credentials """
        self.addHeader('Authorization', 'Basic %s:%s' % (user, password))
        return self


class CommentingLayer(PloneSite):

    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        portal = app.plone

        zcml.load_config('configure.zcml', iqpp.plone.commenting)
        
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-iqpp.plone.commenting:iqpp.plone.commenting')        
        
        # login as admin (copied from `loginAsPortalOwner`)
        uf = app.acl_users
        user = uf.getUserById(PloneTestCase.portal_owner).__of__(uf)
        newSecurityManager(None, user)

        # a commentable document for all tests to play with
        portal.invokeFactory("Document", "document")
        directlyProvides(portal.document, ICommentable)

        portal.invokeFactory("Document", "document2")
        directlyProvides(portal.document2, ICommentable)

        commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        pass


class CommentingMixin:

    def afterSetUp(self):
        self.setRoles(("Manager",))
        self.d = self.portal.document
        self.d2 = self.portal.document2

    def getBrowser(self, logged_in=False):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if logged_in:
            browser.addAuthorizationHeader()
        return browser


class CommentingTestCase(CommentingMixin, PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'iqpp.plone.commenting' product.
    """
    layer = CommentingLayer

class CommentingFunctionalTestCase(CommentingMixin, PloneTestCase.FunctionalTestCase):
    """Base class for functional integration tests for the 'iqpp.plone.commenting' product.
    """
    layer = CommentingLayer
