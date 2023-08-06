betahaus.debug
==============


What is betahaus.debug?
-----------------------
A simple utility function for adding a external pdb script that is accessible via url everywhere in the site.
This does not add any post-mortem debugger. If you want that use the ``Products.PDBDebugMode``.
``betahaus.debug`` only works when in DevelopmentMode.

Installation
------------

buildout:
 - add ``betahaus.debug`` entries to eggs and zcml in the appropriate buildout configuration file.
 - re-run buildout.
 - Install via portal_quickinstaller or Site Setup in plone to get the External method
 
Usage
-----
Add ``/pdb`` to a url and you will get a python debugger on that contenttype where ``self`` is the context.

Remember to remove this when putting in production.

Enjoy!
