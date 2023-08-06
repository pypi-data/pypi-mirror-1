from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from zope.component import getUtility
from collective.portlet.recentactivity.interfaces import IRecentActivityUtility

from Acquisition import aq_inner
from plone.memoize.instance import memoize

from zope.component import getMultiAdapter

from utils import compute_time

import time

class RecentActivityViewlet(ViewletBase):
    index = ViewPageTemplateFile('viewlet.pt')

    @property
    def available(self):
        """Show the portlet only to logged in users.
        """
        context = aq_inner(self.context)        
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return not portal_state.anonymous()
    
    def recent_activities(self):
        """Recent activities, most recent activities come first.
        """
        context = aq_inner(self.context)
        if self._data():     
            for brain in self._data():
                activity = brain[1]
                yield dict(time=compute_time(int(time.time()) - brain[0]),
                           action=activity['action'],
                           user=activity['user'],
                           user_url="%s/author/%s" % (context.portal_url(), activity['user']),
                           object=activity['object'],
                           object_url=activity['object_url'],
                           parent=activity['parent'],
                           parent_url=activity['parent_url'],
                           )
                                        
    def recently_modified_link(self):
        return '%s/@@recent-activity' % self.portal_url
    
    @memoize
    def _data(self):
        # XXX: do we want the limit to be configurable?
        limit = 5
        activities = getUtility(IRecentActivityUtility)
        return activities.getRecentActivity(limit)