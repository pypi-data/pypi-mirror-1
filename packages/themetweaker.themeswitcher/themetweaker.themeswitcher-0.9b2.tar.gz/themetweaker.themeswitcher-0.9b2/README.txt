==================================
themetweaker.themeswitcher Package
==================================

Overview
--------

A product for switching themes on folders (ATFolder and ATBTreeFolder) in Plone.

Author: WebLion Group, Penn State University.

Requirements:

- *plone*: 3.1+
- *sd.common*: (**not on pypi see install instructions**)

Using ThemeSwitcher
-------------------

With quickinstaller installation:

Each folder will have a *ThemeSwitcher* tab that will bring up the switcher form. Here you will be able to choose from a list of installed themes.

Without quickinstaller installation:

Same as with installation except, you will need to manually type the switcher form path. e.g. http://localhost:8080/plonesite/folder1/switcherform, because the actions tabs have not been installed.

Support
-------

Contact WebLion at support@weblion.psu.edu, or visit our IRC channel: #weblion on freenode.net.

Bug reports at http://weblion.psu.edu/trac/weblion/newticket

To Do List *(for developers)*
-----------------------------

- TODO (esteel, pumazi) use gloworm to change viewlet ordering on the subfolder basis [requires that each subfolder have a viewletsettingsstorage (via localconf?)]
- remove the sd.common dependency
- rename to collective.themeswitcher and release into the collective
