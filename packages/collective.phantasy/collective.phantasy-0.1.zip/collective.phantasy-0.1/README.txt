Introduction
============

Change the skin of your plone site, change the skin of any content on the site based on ATFolder, through a simple form.

Just Upload images with the same name in the skin using a tgz or a zip, 
to overload standard plone skin images referenced in css.

At this time, this product is under developpement, do not install on a production site.

Dependencies :
==============
- Plone 3.0x and more
- archetypes.schemaextender 
  (used in this first version to add a referencefield to standard Plone Folders > will not be used in future)
- plone.browserlayer 1.0rc2 if you are on Plone3.0x
- SmartColorWidget (plone3_compat branch on collective svn)
  https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/SmartColorWidget/branches/plone3_compat

In future :    
- z3c.ztresource (not used in this version)
http://pypi.python.org/pypi/z3c.zrtresource/
We will use it in future according to plip  :
http://plone.org/products/plone/roadmap/223

Installation :
==============
With buildout :
- add "collective.phantasy" and "archetypes.schemaextender" in your eggs list
- with plone 3.0x only, add "plone.browserlayer==1.0rc2" in your eggs list, 
- add SmartColorWidget as new Zope2 Product using a subversion recipe :
https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/SmartColorWidget/branches/plone3_compat

In a "classic" Zope instance :
 - TODO


In your plone site > portal_quickinstaller, 
Install "Collective.phantasy"

This will install SmartColorWidget + local browser layer + collective.phantasy

TODO QUICKLY :
=============

- Collective Plone themes using Phantasy (just some examples to show how you can
  make a classic plone theme with dynamic options)

TODO :
======

- Replace ATCT Phantasy Skin contents and @@getPhantasySkin view with zope3 adapters,
events, and all these things about i don't understand nothing.

- Use z3c.ztresource to replace standard page template used for phantasy.css


CHANGELOG :
==========

0.2 - SVN Unreleased
--------------------


0.1
---

* Initial release
