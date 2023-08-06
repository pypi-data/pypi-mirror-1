Introduction
============

Change the skin of your plone site, change the skin of any content on the site based on ATFolder, through a simple form.

Just Upload images with the same name in the skin using a tgz or a zip, 
to overload standard plone skin images referenced in css.

At this time, this product is under developpement, do not install on a production site.

Dependencies :
==============
- Plone 3.1.x and more
- archetypes.schemaextender 
  (used in this first version to add a referencefield to standard Plone Folders)
- Products.SmartColorWidget

In future :    
- z3c.zrtresource (not used in this version)
http://pypi.python.org/pypi/z3c.zrtresource/
We will use it in future according to plip  :
http://plone.org/products/plone/roadmap/223

Installation :
==============
read docs/INSTALL.txt inside product install it in your Zope instance

Then in your Plone Site, use portal_quick_installer to install it, this will also install
SmartColorWidget.

TODO QUICKLY :
=============

- Collective Plone themes using Phantasy (just some examples to show how you can
  make a classic plone theme with dynamic options)

TODO :
======

- Replace ATCT Phantasy Skin contents and getPhantasySkin view with zope3 adapters,
events, and all these wonderful things, when i will be able to do that.

- Use z3c.ztresource to replace standard page template used for phantasy.css


