# -*- encoding: utf-8 -*-

import time

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from zope.component import getUtility

from collective.portlet.recentactivity import RecentActivityPortletMessageFactory as _

from collective.portlet.recentactivity.interfaces import IRecentActivityUtility

from collective.portlet.recentactivity.interfaces import IRecentActivityPortlet

from utils import compute_time

class IRecentActivityPortlet(IPortletDataProvider):
    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)


class Assignment(base.Assignment):
    implements(IRecentActivityPortlet)

    def __init__(self, count=5):
        self.count = count

    @property
    def title(self):
        return _(u"Recent Activity Portlet")

class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentActivityPortlet)
    label = _(u"Add Recent Activity Portlet")
    description = _(u"This portlet displays recently modified content.")

    def create(self, data):
        return Assignment(count=data.get('count', 5))

class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentActivityPortlet)
    label = _(u"Edit Recent Portlet")
    description = _(u"This portlet displays recently modified content.")

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('portlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()  # whether or not the current user is Anonymous
        self.portal_url = portal_state.portal_url()  # the URL of the portal object

        # a list of portal types considered "end user" types
        self.typesToShow = portal_state.friendly_types()  

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

    def render(self):
        return self._template()

    @property
    def available(self):
        """Show the portlet only if there are one or more elements."""
        return not self.anonymous

    def has_recent_activities(self):
        return self._data()
        
    @memoize
    def recent_activities(self):
        context = aq_inner(self.context)
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
        limit = self.data.count
        activities = getUtility(IRecentActivityUtility)
        return activities.getRecentActivity(limit)

