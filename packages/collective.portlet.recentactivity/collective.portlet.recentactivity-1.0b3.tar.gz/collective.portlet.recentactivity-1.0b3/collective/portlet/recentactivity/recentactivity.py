from datetime import datetime
import logging
import Globals
import os.path
from AccessControl import getSecurityManager,ClassSecurityInfo
from Products.Five import BrowserView

from zope.component import getUtility

from Acquisition import aq_parent
from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner

from collective.portlet.recentactivity.interfaces import IRecentActivityUtility

from zope.component import getUtility
from collective.portlet.recentactivity.interfaces import IRecentActivityUtility


class RecentActivityView(BrowserView):

    template = ViewPageTemplateFile('recentactivity.pt')

    def __call__(self):
        """View the recent activity on a separate page.
        """
        self.request.set('disable_border', True)
        return self.template()

    def recent_activities(self):
        context = aq_inner(self.context)
        u = getUtility(IRecentActivityUtility)
        return u.getRecentActivity(5)
