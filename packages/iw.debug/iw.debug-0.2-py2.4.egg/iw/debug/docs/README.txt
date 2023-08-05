================
iw.debug package
================

.. contents::

What is iw.debug
----------------

This package allow you to start the python debugger (pdb) or the ipython
debugger (ipdb) on any objects in zope.
For that you have to add /pdb to the url of any object. And if your zope
instance is in debug mode it will start the (i)pdb in your terminal.

Exploring objects
-----------------

Run your zope instance in foreground::

  ./bin/zopectl fg

Call an url ended with /pdb::

  wget http://localhost:8080/portal/pdb

Then you get (i)pdb prompt in your console::

  ipdb> 

Typing `ll` will show you a few locals::

  ipdb> ll
  Out[0]: 
  {'context': <PloneSite at /portal>,
   'meth': None,
   'portal': <PloneSite at /portal>,
   'request': <HTTPRequest, URL=http://localhost:8080/portal/@@pdb/pdb>,
   'view': None}

Debuging objects views and methods
----------------------------------

You can also use a query string in the url to debug a callable::

  wget http://localhost:8080/portal/pdb?v=__repr__

Then back to your console::

  ipdb> ll
  Out[0]: 
  {'context': <PloneSite at /portal>,
   'meth': <bound method PloneSite.__repr__ of <PloneSite at /portal>>,
   'portal': <PloneSite at /portal>,
   'request': <HTTPRequest, URL=http://localhost:8080/portal/@@pdb/pdb>,
   'view': None}

If a browser view is found, then it will be used as callable::

  wget http://localhost:8080/portal/pdb?v=rules-controlpanel

Then back to your console::

  ipdb> ll
  ipdb> Out[0]: 
  {'context': <PloneSite at /portal>,
   'meth': None,
   'portal': <PloneSite at /portal>,
   'request': <HTTPRequest, URL=http://localhost:8080/portal/@@pdb/pdb>,
   'view': <Products.Five.metaclass.ContentRulesControlPanel object at ...>}


For both view and callable, you can enter in it by typing s::

  ipdb> s
  ipdb> --Call--
  > /../plone/app/contentrules/browser/controlpanel.py(18)__call__()
       17 
  ---> 18     def __call__(self):
       19         form = self.request.form

If you want to pass extra args to the callable do something like::

  wget http://localhost:8080/portal/pdb?v=myview&arg1=value1&arg2:int=2

Extra args will be passed to the callable as keyword arguments.

Add iw.debug to your plone3 buildout
------------------------------------

In the [buildout] section of your buildout.cfg add::

  [buildout]
  ...
  # Add additional eggs here
  # elementtree is required by Plone
  eggs =
    elementtree
    iw.debug
    ...

Then in the [instance] section::

  [instance]
  ...
  # If you want to register ZCML slugs for any packages, list them here.
  # e.g. zcml = my.package my.other.package
  zcml = iw.debug
         ...


