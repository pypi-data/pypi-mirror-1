from collective.portlet.recentactivity.tests.base import TestCase

from Products.CMFCore.utils import getToolByName

from collective.portlet.recentactivity.utils import *

class TestComputeTime(TestCase):

    def test_seconds(self):
        self.assertEquals(compute_time(12), 
                          {'hours': 0, 'minutes': 0, 'days': 0})

    def test_minutes(self):
        self.assertEquals(compute_time(62),
                          {'hours': 0, 'minutes': 1, 'days': 0})

    def test_hours(self):
        self.assertEquals(compute_time(7260), 
                          {'hours': 2, 'minutes': 1, 'days': 0})

    def test_days(self):
        # 1 day = 86400 seconds
        # 2 days = 172800 seconds
        # 1 hour = 3600 seconds
        self.assertEquals(compute_time(172800),
                          {'hours': 0, 'minutes': 0, 'days': 2})

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestComputeTime))
    return suite