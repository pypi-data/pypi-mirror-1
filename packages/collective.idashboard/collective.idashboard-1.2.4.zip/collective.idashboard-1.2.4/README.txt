Introduction
============
Pimp your Plone dashboard!

This is a Plone Product that makes your users' Plone dashboard behave similarly to the iGoogle dashboard.

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

Add 'slc.idashboard' egg to the [instance] part in your buildout configure::

    eggs =
        collective.idashboard


Upgrading from <=1.2.2:
=============================

From version 1.2.3 onwards, overrides.zcml is no longer used, so make sure you
*remove* the following from the 'zcml' subsection in your [instance] section::
    
    zcml =
        collective.idashboard
        collective.idashboard-overrides

Make sure that you run the import step in the Plone Control Panel. Just click
on the button next to 'Upgrade:'. Drag and drop will not be enabled if you forget to do this.


TODO
====

* Add sticky mininize/maximise 

