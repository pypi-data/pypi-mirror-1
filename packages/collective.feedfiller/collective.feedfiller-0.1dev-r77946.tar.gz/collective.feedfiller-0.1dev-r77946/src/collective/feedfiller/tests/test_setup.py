import unittest
from collective.feedfiller.tests.base import CollectiveFeedfillerTestCase

from Products.CMFCore.utils import getToolByName

class TestSetup(CollectiveFeedfillerTestCase):
    
    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')
    
        
    def test_feedfeeder_installed(self):
        self.failUnless('FeedFeederItem' in self.types.objectIds())
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
