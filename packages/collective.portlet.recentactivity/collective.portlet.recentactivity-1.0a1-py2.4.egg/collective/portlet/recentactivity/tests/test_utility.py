from collective.portlet.recentactivity.tests.base import TestCase

from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

from Acquisition import aq_parent, aq_base

from datetime import datetime, timedelta

from zope.component import getUtility

from collective.portlet.recentactivity.interfaces import IRecentActivityUtility
from collective.portlet.recentactivity.utilities import RecentActivityUtility


class TestRecentActivityUtility(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.activities = getUtility(IRecentActivityUtility)
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        
    def testAddActivity(self):
        # Add an activity and make sure the method
        # returns an int timestamp
        activity = self.activities.addActivity(
                       DateTime(),
                       "added",
                       "johndoe",
                       self.portal.doc1,
                       aq_parent(self.portal.doc1)
                    )
        self.failUnless(activity)
        self.assert_(activity - int(DateTime() < 10))
    
    def testRecentActivity(self):
        # Add an activity and make sure all the
        # necessary data is stored in the utility
        activity = self.activities.addActivity(
                       DateTime(),
                       "added",
                       "johndoe",
                       self.portal.doc1,
                       aq_parent(self.portal.doc1)
                    )
        activities = self.activities.getRecentActivity()

        self.assertEquals(len(activities), 1)
        self.assertEquals(activities[0][0], (activity - int(DateTime() < 10)))
        self.assertEquals(activities[0][1]['action'], 'added')
        self.assertEquals(aq_base(activities[0][1]['object']), aq_base(self.portal.doc1))
        self.assertEquals(activities[0][1]['object_url'], 'http://nohost/plone/doc1')
        self.assertEquals(aq_base(activities[0][1]['parent']), aq_base(self.portal))
        self.assertEquals(activities[0][1]['parent_url'], 'http://nohost/plone')
        self.assertEquals(activities[0][1]['user'], 'johndoe')

        # Add another activity
        new_id = self.activities.addActivity(
                       DateTime() + 1,
                       "edited",
                       "johndoe",
                       self.portal.doc1,
                       aq_parent(self.portal.doc1)
                    )        

        act = self.activities.getRecentActivity()
        
        #self.assertEquals(len(act), 2)
                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRecentActivityUtility))
    return suite