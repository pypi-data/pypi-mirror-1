from zope import schema

from zope.interface import Interface, Attribute
from plone.portlets.interfaces import IPortletDataProvider
from collective.portlet.recentactivity import RecentActivityPortletMessageFactory as _


class IRecentActivityPortlet(IPortletDataProvider):
    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)

class IRecentActivityUtility(Interface):
    """ Utility to store recent activity.
    """

    #activities = Attribute(u"Tree of activities")

    def addActivity(timestamp, action, user, object, parent):
        """Add an activity to the log.
        """

    def getRecentActivity(items):
        """Get recent activities.
        """

