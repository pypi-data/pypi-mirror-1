import unittest

from AccessControl import Unauthorized

from collective.portlet.recentactivity.tests.base import TestCase

from collective.portlet.recentactivity.viewlet import RecentActivityViewlet

from Products.CMFCore.utils import getToolByName

class TestRecentActivityViewlet(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.setRoles(['Manager',])

    def testRecentActivityViewlet(self):
        request = self.app.REQUEST
        viewlet = RecentActivityViewlet(self.portal, request, None, None)
        viewlet.update()
        #self.assertRaises(Unauthorized, viewlet.render(), '@@view')        

        # Add activity and check if it is in the portlet
        request = self.app.REQUEST
        viewlet = RecentActivityViewlet(self.portal, request, None, None)
        viewlet.update()
        #result = viewlet.render()
        #self.failIf("<link" not in result)
        #self.failIf("http://nohost/plone/RSS" not in result)


    def test_recent_activities(self):
        pass
    
    def test_available(self):
        pass
    
    def test_recently_modified_link(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRecentActivityViewlet))
#    suite.addTest(makeSuite(TestRenderer))
    return suite