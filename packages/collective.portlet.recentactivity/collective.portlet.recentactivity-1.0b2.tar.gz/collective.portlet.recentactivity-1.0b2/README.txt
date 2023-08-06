Introduction
============

collective.portlet.recentactivity provides a Portlet and a Viewlet
with Facebook like entries on recent user activities, e.g. "the 
user admin added 'News Item 1' to 'News' 10 minutes ago".

By default, the Recent Activity Viewlet is not registered. If you want
to register it, for example below your content, you have to add this
code to your configure.zcml::

	<browser:viewlet
        name="collective.portlet.recentactivity.RecentActivityViewlet"
        manager="plone.app.layout.viewlets.interfaces.IBelowContentBody"
        class=".viewlet.RecentActivityViewlet"
        permission="zope2.View"
        />


Buildout Installation
=====================

To install collective.portlet.recentactivity, add the following code 
to your buildout.cfg::

    [instance]
    ...
    eggs =
        ...
        collective.portlet.recentactivity

    ...

    zcml =
        ...
        collective.portlet.recentactivity


Known Issues
============

The log entries only work for Archetype content types. Though, it 
should be fairly easy to replace the Archetype specific event handlers
with ones that work for other types of content.
