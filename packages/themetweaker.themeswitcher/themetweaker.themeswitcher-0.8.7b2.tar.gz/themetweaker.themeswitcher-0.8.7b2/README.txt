==================================
themetweaker.themeswitcher Package
==================================

Overview
--------
A product for switching themes on folders (ATFolder and ATBTreeFolder) in Plone.

Author: WebLion Group, Penn State University.

Requirements:

- *plone* 3.?.?
- *sd.common*: (**not on pypi**) ``svn checkout http://tracker.trollfot.org/svn/projects/sd.common/trunk/ sd.common``
- *z3c.unconfigure* 1.0.1: (included from setup.py) http://pypi.python.org/pypi/z3c.unconfigure/1.0.1
- *plone.browserlayer* 1.0.0: (included from setup.py) http://pypi.python.org/pypi/plone.browserlayer/1.0.0

Using ThemeSwitcher
-------------------
With quickinstaller installation:
    Each folder will have a *ThemeSwitcher* tab that will bring up the switcher form. Here you will be able to choose from a list of installed themes that use browserlayer to register themselves. How do I know if the theme is registered as a browserlayer? Look to see if the theme contains a ``browserlayer.xml`` file, if it does, chances are it is registered as a browserlayer.

Without quickinstaller installation:
    Same as with installation except, you will need to manually type the switcher form path. e.g. http://localhost:8080/plonesite/folder1/switcherform, because the actions tabs have not been installed.

Support
-------
Contact WebLion at support@weblion.psu.edu, or visit our IRC channel: #weblion on freenode.net.

Bug reports at http://weblion.psu.edu/trac/weblion/newticket

To Do List *(for developer)*
----------------------------

- TODO (pumazi) uninstall of a themeswitcher instance will be difficult since the IThemeSpecific interface will be placed on a bunch of folders... We need something to catalog what has this interface or something that will iterate over everything themeswitcher adapts (ATFolder and ATBTreeFolder) to check if IThemeSwitcher is provided by that object
- TODO (esteel, pumazi) use gloworm to change viewlet ordering on the subfolder basis [requires that each subfolder have a viewletsettingsstorage (via localconf?)]
