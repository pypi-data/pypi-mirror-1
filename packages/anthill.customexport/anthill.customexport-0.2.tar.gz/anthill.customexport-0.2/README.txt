Introduction
------------

This package adds a new tab to ``portal_skins/custom`` folder named "FS-Export". 
Using this tab you can export all scripts and other stuff you have customized
with one click to the filesystem. Now also with support for
portal_view_customizations folder.

Even in times of views, content providers and viewlets there are cases where
you have stuff in custom folder and struggle with exporting it to the
filesystem. 

Installation
------------

- Extend your buildout with anthill.customexport
- Make sure your instance knows about it (eggs=, zcml=)
- Rerun buildout
- Go to portal_skins/custom and then click on the new tab

Tested with
-----------

Plone 2.5.x and 3.x
