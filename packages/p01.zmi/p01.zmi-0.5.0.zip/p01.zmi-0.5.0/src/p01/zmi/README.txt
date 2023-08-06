======
README
======

This package contains a Zope Application Management skin. This skin supports 
a modular application management UI without any dependency. The goal of this
skin is to support a skin which offers a set of management components without
to install something in your site.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the page.html view which is registred in the
ftesting.zcml file with our skin:

  >>> manager = Browser()
  >>> manager.handleErrors = False
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++ZMITesting'
  >>> manager.open(skinURL + '/index.html')
  >>> manager.url
  'http://localhost/++skin++ZMITesting/index.html'


Runtime management
------------------

Now let''s test the different pages we have available by default. first let's 
check the process page:

  >>> manager.open(skinURL + '/runtime.html')


ZODB control
------------

The ZODB control page offers packing the DB

  >>> manager.open(skinURL + '/ZODBControl.html')


Gnerations
----------

And the generations page shows pending generation steps:

  >>> manager.open(skinURL + '/generations.html')


Error logging
-------------

We also have an error log and management page available at:

  >>> manager.open(skinURL + '/errors.html')

You can configure the error log handling et the error utility edit page.
but forst we need a INegotiator utility for this page:

  >>> import zope.component
  >>> from zope.i18n.interfaces import INegotiator
  >>> from zope.i18n.negotiator import negotiator
  >>> zope.component.provideUtility(negotiator, INegotiator)

  >>> manager.open(skinURL + '/editError.html')


Registration
------------

the object registration page is also available:

  >>> manager.open(skinURL + '/registration.html')

