Introduction
============
Pimp your Plone dashboard!

This is a Plone Product that makes your user dashboard behave similarly to the iGoogle dashboard.

Specifically, it adds the following functionality:
   - Drag and drop portlets within and between rows
   - Ajax enabled inline portlet editing and saving
   - Ajax removal/deletion of portlets with themable confirmation modal dialog.
   - Toggle show/hide portlets


Dependencies
============

**collective.js.jquery**

This product requires JQuery 1.3.2 which is currently not part of the latest Plone Release.
The JQuery 1.3.2 source code is bundled in this released but the xml and zcml directives for registering it has been disabled.
Instead you should use collective.js.jquery. See the included buildout.cfg.

WARNING: Installing collective.js.jquery without enabling JQuery 1.3.2 (as
bundled in collective.idashboard, or through collective.js.jquery) will not
enable *any* of the Ajax features.

Install
=======

collective.idashboard uses overrides.zcml, so make sure you add the following to your buildout.cfg:

[instance]

zcml = collective.idashboard-overrides

When adding a new Plone site, choose both the JQuery and the collective.idashboard profiles.


Acknowledgements
================

This product is a rewrite of a product initially written by me for Upfront Systems. http://www.upfrontsystems.co.za

Thanks goes out to Roche Compaan (roche@upfrontsystems.co.za) for his help and assistance.

TODO
====

Install collective.js.jquery through setuphandlers
Add new icons
Add sticky mininize/maximise 
Add css class change for minimise button.
Move header button images out to css.


