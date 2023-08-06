Grok based WSGI application without ZODB
========================================

The application uses the new zope.publisher.paste package, 
a custom Root object and a custom publication. 
Runs Grok as WSGI app.

Requirements
------------

I run the package with a Grok trunk checkout and Python2.5


Installation
------------

Checkout 'd2m.wsgiapp' to your buildout root folder.
Add the 'd2m.wsgiapp/etc' folder to your buildout root folder.

Modify buildout.cfg like so:

[buildout]
develop = <...> d2m.wsgiapp
<...>

[app]
recipe = zc.recipe.egg
eggs = d2m.wsgiapp
       z3c.evalexception>=2.0
       Paste
       PasteScript
       PasteDeploy
interpreter = python
<...>

Run bin/buildout.


Run the application
-------------------

Run bin/paster serve etc/debug.ini

ZMI and grok.admin views are not available atm. Your Grok app should work though.

Credits
-------
Thanks to Philipp von Weitershausen for his IRC support.