================
Mlango Dashboard
================

This package contains the Mlango drop-in replacement for the standard Plone
dashboard. The package needs some overrides (configured in overrides.zcml) to
enable drop in replacement. The package overrides:

* the default portletmanagerrenderer
* the edit manager for dashboard, to allow filter on non allowed portlets
  as defined by the mlango manager tool.
* the dashboard view
* the base Assignment class, to allow annotations on the assignment.
* The template for group settings, prefs_group_details


Audience
--------

The product is targeted for Plone 3.1. For 3.0, you may need to install
jquery.


Dashboard
---------

Basically, Mlango adds drag-n-drop capabilities to your
dashboard. There's a little more though... Mlango gives you a tool or
rather configlet to set the number of columns the user gets to see on
his/her dashboard, and enables an administrative user to filter
allowed portlets for a user. The settings are configurable as a
configlet in website settings.


Groups
------

The Mlango product adds group dashboard to Plone. The group dashboard
adds group portlets to the user dashboard as fixed portlets. To get to
the group dashboard settings, just go to user/group management in the
website settings, pick a group, and select the tab 'group dashboard',
as administrative user.


Remember/Membrane
-----------------

The group implementation of Remember is slightly odd, in that it doesn't
use the group assignments for a user that are set in acl_users.
You may want to create your own member class, and fix that, using the following
snippets:


from Products.membrane.interfaces import IMembraneGroupManagerPlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
...
# optional?
del schema['groups']
...

class MyMember(Member):

    ...

    security.declarePublic('getGroups')
    def getGroups(self):
        pas = getToolByName(self, 'acl_users')
        groups = ()
        plugins = pas.plugins.listPlugins(IGroupsPlugin)
        for id, plugin in plugins:
            if not IMembraneGroupManagerPlugin.providedBy(plugin):
                groups = groups + plugin.getGroupsForPrincipal(self)
        return list(groups)

    ...