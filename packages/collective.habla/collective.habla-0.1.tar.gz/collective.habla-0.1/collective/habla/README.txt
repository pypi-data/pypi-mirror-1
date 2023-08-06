collective.habla
================

Overview
--------
This plugin integrates hab.la web chat in a Plone portal.
To use hab.la chat you should register an account at http://www.hab.la/ website.

Requirements
------------
 plone >= 3.2.1
 plone.app.registry >= 1.0a1

For more information: http://www.hab.la/

Tests
-----

We start the tests with the usual boilerplate
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> self.portal.error_log._ignored_exceptions = ()


Check the existance of collective.habla.habla_id.
    >>> from plone.registry.interfaces import IRegistry
    >>> from zope.component import getUtility
    >>> settings = getUtility(IRegistry)
    >>> settings.records['collective.habla.habla_id']
    <Record collective.habla.habla_id>

It holds Hab.la UserID in the Plone registry. 
    >>> habla_id = settings.records['collective.habla.habla_id'].value
    >>> habla_id
    u'0000-00000000-00-0000'

Check inclusion of necessary javascript to enable Hab.la services only
for the objects that implment IHablaChat interface
    >>> browser.open(portal_url)
    >>> '<script type="text/javascript" src="http://static.hab.la/js/wc.js"></script>' in browser.contents
    False

Now we mark the front-page Document with the IHablaChat interface and refresh the page
    >>> from collective.habla.interfaces import IHablaChat
    >>> from Products.Five.utilities.marker import mark
    >>> mark(portal['front-page'], IHablaChat)
    >>> browser.open(portal_url)

We can see the corrects javascripts
    >>> '<script type="text/javascript" src="http://static.hab.la/js/wc.js"></script>' in browser.contents
    True
    >>> '<script type="text/javascript">wc_init(\'%s\');</script>' % habla_id.encode('utf8') in browser.contents
    True

When we un-mark front-page the web chat scripts disappear.
    >>> from Products.Five.utilities.marker import erase
    >>> erase(portal['front-page'], IHablaChat)
    >>> browser.open(portal_url)
    >>> '<script type="text/javascript" src="http://static.hab.la/js/wc.js"></script>' in browser.contents
    False
