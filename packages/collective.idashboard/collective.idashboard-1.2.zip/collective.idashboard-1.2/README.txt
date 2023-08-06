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

* http://pypi.python.org/pypi/collective.js.jquery
* http://pypi.python.org/pypi/collective.js.jqueryui
* http://pypi.python.org/pypi/collective.alerts

Install
=======

collective.idashboard uses overrides.zcml, so make sure you add the following to your buildout.cfg::

  [instance]
  ...
  zcml = collective.idashboard-overrides

Default profile imports also profile of dependencies

TODO
====

* Add sticky mininize/maximise 
