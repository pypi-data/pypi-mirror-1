Introduction
============

If you are using for any reason `p4a.subtyper`__, your Plone site will show in every page a not very
nice "*Sub-types*" menu, even if the menu is empty.

__ http://pypi.python.org/pypi/p4a.subtyper/

This "product" will remove it using a very little jQuery code.

You have available 2 different approach:

`show invisible menu` (default)
  This will show the menu that a CSS given and installed with this product hide.
  So the Subtyper menu is always hidden, but Javascript restore it when needed.
     
  In this way you will not see "blink" effect in the page.

`hide visible menu`
  This seems simpler, just hide the menu when is empty, but this way in every page where
  the menu is empty, you'll see it disappear.
     
  To enable this way of handle the menu, just disable the *hide_subtypes.css* CSS
  in *portal_css*

TODO
----

* An uninstall Generic setup step.

 