ore.wsgiapp
-----------

This packages allows one to bootstrap a zope3 environment as a wsgi
application without a ZODB.

Users of this package instead register the root object to be published
as an IApplication utility, which is looked up and returned by the
default publication. All object publishing/traversal continues on from 
this user defined root object.

In addition, this package supports standard zope3 zcml loading, and debug features.

Usage
-----

A brief tutorial in using ore.wsgiapp to construct applications


Define an Application
=====================


First we need to define an object which implements IApplication, which will
be the root of our published application, useful base classes for this purpose 
are in the ore.wsgiapp.app module.

  >>> from ore.wsgiapp import app
  >>> class MyApplication( app.Application ): pass

now if we register this object as a utility it will be the root object
published by zope.

  >>> provideUtility( MyApplication )
 
you will still need to provide views, subobjects, etc.
  
Paste Configuration
===================

To use with Paste, you include a configuration section like::

where:

  [app:zope]
  use = egg:ore.wsgiapp
  zcml = test.zcml
  
Application
===========

Its often useful to defer application setup till after the application has finished loading its 
configuration, so that component architecture is fully configured. in order to allow for this, ore.wsgiapp
generates a IWSGIApplicationCreatedEvent with the application as an attribute. we can register a subscriber
for this in zcml, and it will be invoked after configuration is loaded. 

As an example we'll use an event subscriber to 

  >>> from zope.app.component import site
  >>> from zope.app.container.sample import SampleContainer
  >>>
  >>> def appSetUp( app, eventevent ):
  ...    """Initialize an application"""
  ...
  ...    # setup a local site manager
  ...    sm = site.LocalSiteManager( self.context )
  ...    self.context.setSiteManager( sm )
  ...
  ...    # add a folder
  ...    app['news'] = SampleContainer()

  
PDB Debug Mode
==============

A useful facility for application development supported by ore.wsgiapp is to allow the application
to automatically drop into a post mortem debugging session, in the python debugger, on an unhandled
exception in the application. ore.wsgiapp supports pdb debug mode, simply by turning on the developer
mode configuration. The developer mode also enables other features in the zope stack, such as automatic
reloading of page templates, etc.

  [app:main]
  use = egg:zope.publisher
  publication = egg:zope.publisher#sample
  foo = bar

Detailed example
================

There's a sample application class in ore.wsgiapp.tests.TestApp, along with a simple default view
ore.wsgiapp.tests.AppView. We setup 

    >>> test_zcml_contents

We can create a WSGI application for this application by calling the ore.wsgiapp paste application
factory. This app accepts zcml keyword arg to point to a initial application configuration, and a devmode boolean switch. We'll get the factory by looking it up with package resources:

    >>> import pkg_resources
    >>> app_factory = pkg_resources.load_entry_point(
    ...     'ore.wsgiapp', 'paste.app_factory', 'main')
    
    >>> app = app_factory(dict(global_option=42), 
    ...                   zcml=test_zcml_path)


We can perform a test web request by calling the app factory with an
environment dictionary and a start-response function:

    >>> def start_response(status, headers):
    ...     print status
    >>> import cStringIO
    >>> env = {'CONTENT_TYPE': 'text/plain', 'PATH_INFO': '/',
    ...        'REQUEST_METHOD': 'GET', 'wsgi.input':  cStringIO.StringIO('')}

    >>> for data in app(env, start_response):
    ...     print data,
    ... # doctest: +NORMALIZE_WHITESPACE
    200 Ok
    Hello World
