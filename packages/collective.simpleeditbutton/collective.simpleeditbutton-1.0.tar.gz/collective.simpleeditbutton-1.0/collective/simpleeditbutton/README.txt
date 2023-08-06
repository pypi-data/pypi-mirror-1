Introduction
============

This package is intended to simplify the Plone editing interface for casual
visitors who are allowed to contribute content but are not necessarily fully
trained on the Plone user interface.

It overrides the standard Plone "contentviews" and "contentactions" viewlets
so that the full set of tabs and actions are only shown for users with the
'View complete edit interface' permission.  This permission is enabled for the
Manager, Editor, and Reviewer roles by default.  Users who lack this permission
will only see an edit tab even if they have permission to access other tabs
and actions.

This adjustment is generally only useful if you have modified your site workflow
to allow some content contributed by users with the Member or similar roles.

The normal set of tabs and actions is still available on views other than the
default view.

Compatibility
-------------

This package has been tested with Plone 3.1.7, but I believe it should work
in 3.1, 3.2, and 3.3 (not 3.0).

Installation
------------

Add the collective.simpleeditbutton egg to your buildout and restart Zope.
If using Plone < 3.3, you must also have buildout generate a ZCML slug for
collective.simpleeditbutton.

Install 'Simple edit button for Plone' in the quick installer or add/remove
products configlet.
