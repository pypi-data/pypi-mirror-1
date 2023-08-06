SplashDancing
===================
SplashDancing aka Sensible Defaults
Aims to add some "sensible defaults" to the Singing And Dancing Product

The features include:
------------------------
- pictures sent with news items
- A control panel for "zapping" HTML ids and classes that should not show up in newsletters

More detail
------------------
This product registers an adapter for the Singing and Dancing newsletter product that detects 
if a news item has a picture and sends the picture along with the news item.
It also provides a "through the web" (TTW), control panel where a user can list ids and classes
that should not be sent in a newsletter.

An Out of the box S&D newsletter does not allow newsitems to "travel" with their pictures and instead has a very basic representation of newsitems.

It is based on ZopeSkel's 'paster create -t archetype' which is a bit overkill, but it provided all the necessary "hooks"
to get started.

- Code repository: http://svn.plone.org/svn/collective/collective.splashdancing
- Questions and comments can be sent to the singing and dancing mailing list (http://groups.google.com/group/singing-dancing) 

Warning, There be Dragons
----------------------------
This system works, however it will, hopefully, be refactored in the near future (by early 2010). It has only been tested with Singing and Dancing 8.12 on OS X Leopard. There is no test coverage for this code, so consider it broken.
