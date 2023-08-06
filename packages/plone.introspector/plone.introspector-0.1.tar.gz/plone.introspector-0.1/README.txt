plone.introspector
******************

What is plone.introspector?
===========================

'plone.introspector' is the Zope2/Plone UI for zope.introspector. 
It provides a way to search and browse the component registry.


'plone.introspector' started by Martin Lundwall (Student) and Lennart Regebro (Mentor) 
as part of the Google Summer of Code 2008. 

The base libraries 'zope.introspector' and 'zope.introspectorui' was developed
togeher wth another GSOC 2008 student Uli Fouquet, with mentor Martijn Faassen.


Using plone.introspector
===========================
Currently you can browse and search the component registry via the ZMI.

Go to http://localhost:8080/manage and there is a tab called
'Component Registry' where you can search the registry for entries of Adapter,
Handler, Utility or Subscription Adapter.

You can also browse all of the registry (since the registry often have many entries 
the browe page might be slow on loading) by clicking on the 'browse the registry here.' link.
Who would have thought that?

Using the browse page you can see all registrations in their respective namespace.
You can find a registration under all involved interfaces. 

example:
The adapter below is listed under all of the following interfaces

* zope.viewlet.interfaces.IViewlet
* zope.publisher.interfaces.browser.IBrowserView
* zope.interface.Interface
* zope.publisher.interfaces.browser.IDefaultBrowserLayer

and
 
* plone.app.layout.viewlets.interfaces.IPortalTop

#
Adapter: header
Factory

    * SimpleViewletClass from /Users/martin/.buildout/eggs/plone.app.layout-1.1.5-py2.4.egg/plone/app/layout/viewlets/portal_header.pt

Provided Interface

    * zope.viewlet.interfaces.IViewlet

Required Interfaces

    * zope.interface.Interface
    * zope.publisher.interfaces.browser.IDefaultBrowserLayer
    * zope.publisher.interfaces.browser.IBrowserView
    * plone.app.layout.viewlets.interfaces.IPortalTop


This makes it easy to find and make sure that all interface registrations are correct,
and maybe find the reason why something doesn't show up as supposed to.

Installing zope.introspector
============================

User Installation:
-----------------

To use plone.introspector do the following:

Add plone.introspector to the "eggs" part of the buildout config file. 
You also need to add a "zcml" slug in the instance part.

[buildout]
eggs = 
	plone.introspector
	
A bit further down in the confinguration file.
 
[instance]
zcml = 
	plone.introspector 
	

Now when you run ./bin/buildout plone.introspector will get downloaded and installed.


Development installation:
------------------------
If you want to extend, modify or check out the code you should do the following:

Checkout the source and add it to you src folder in the buildout.

svn co https://svn.plone.org/svn/collective/plone.introspector/trunk plone.introspector

In the buildout configuration file you add a "development" statement to the buildout part as well as the above mentioned entries.

[buildout]
eggs = 
	plone.introspector

develop = 
   src/plone.introspector
	
A bit further down in the confinguration file.
 
[instance]
zcml = 
	plone.introspector 
