Introduction
============

This plugin integrate hab.la web chat in a Plone portal.
To use hab.la chat you should register an account at http://www.hab.la/ website.

Requirements
------------
 * plone >= 3.2.1
 * plone.app.registry >= 1.0a1

For more information: http://www.hab.la/

Usage
=====
Dependencies are not specified in setup.py. You should add this to your buildout: ::

	[buildout]
        ...
	eggs = 
	    collective.habla
	    zope.i18n>=3.4
	    plone.app.registry
        ...
	[instance]
        ...
	zcml = 
	    collective.habla


Install this product from the Plone control panel.
Get an account id at http://www.hab.la/ of the form 0000-00000000-00-0000
Look for "Habla User Id" in the "configuration registry" in the Plone control panel
and paste your account id.

To enable the chat in a page navigate to that page, and choose "Enable chat" from the Actions menu.
The chat will show for every user viewing that page.
To disable it, click on "Disable chat" in the actions menu.

Contributors
============

* Giorgio Borelli - gborelli
* Silvio Tomatis - silviot

Known issues
============
After product reinstall the configuration registry entry doesn't work.
Reinstalling plone.app.registry as well solves the problem.



