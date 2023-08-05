ore.wsgiapp
-----------

This packages allows one to bootstrap a zope3 environment as a wsgi
application without a ZODB.

Users of this package instead register the root object to be published
as an IApplication utility, which is looked up and returned by the
default publication. All object publishing/traversal continues on from 
this utility.


usage
-----

define an object which implements IApplication, useful base classes for
this purpose are in the app.py module.

  >>> from ore.wsgiapp import app
  >>> class MyApplication( app.Application ): pass

now if we register this object as a utility it will be the root object
published by zope.

  >>> provideUtility( MyApplication )
 
you will still need to provide views, subobjects, etc.
  
