Introduction
============

This package adds the ability to manage dashboard portlets on a per-group
basis. Once installed, a site manager will be able go to the "Group Portlets"
tab when editing a group and then click the "Edit group dashboard portlets"
link. From here, group dashboard portlets can be assigned as normal.

Any member in that group will then see the relevant portlets on their
dashboard. Note that group portlets will appear below the user's own portlets.

To make it easier to lock down the dashboard, the view and edit permissions
have been separated. You can take away the "Portlets: Manage own portlets"
permission to let users view the dashboard without the ability to edit it.

Installation
============

Install as normal. You will need to load a ZCML slug unless you are using
Plone 3.3, in which case it should be loaded automatically.

If you get a version conflict in zope.component or similar, add this to
your versions block::

    [buildout]
    ...
    versions = versions
    ...

    [versions]
    ...
    zope.component = 3.4.0
    zope.securitypolicy = 3.4.0
    ...
