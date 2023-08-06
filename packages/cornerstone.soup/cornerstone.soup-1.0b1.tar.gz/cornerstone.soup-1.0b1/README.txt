Overview
========

cornerstone.soup provides a container for persistent records which are
queryable. The code is tested with Plone3.3 but should work with any Zope2.10+
application, as long as the appropriate utilities are provided via persistent
local components.

Usage
=====

Subclass the Soup object and give it an appropriate id.:

  >>> from cornerstone.soup import Soup
  >>> class MySoup(Soup):
  ...     id = u'mysoup'

We have to provide a Catalog Factory for our soup.:

  >>> from zope.interface import implements
  >>> from zope.catalog.catalog import Catalog
  >>> from zope.catalog.field import FieldIndex
  >>> from cornerstone.soup.interfaces import ICatalogFactory
  >>> class MyCatalogFactory(object):
  ...     implements(ICatalogFactory)
  ...
  ...     def __call__(self):
  ...         catalog = Catalog()
  ...         catalog[u'name'] = FieldIndex(field_name='name',
  ...                                       field_callable=False)
  ...         return catalog

Now, 3 things have to be registered under the same name:

  * the catalog factory for this soup
  * the specific soup
  * a five.intid.intid.OFSIntIds object

Register the ``ICatalogFactory`` as utility via ZCML.:

  <utility
    name="mysoup"
    factory=".mymodule.MyCatalogFactory"
    provides="cornerstone.soup.interfaces.ICatalogFactory"
  />

The ``IIntIds`` and ``ISoup`` utilities are registered as local components.
  
In Plone you can easily register you local components via GenericSetup.
Therefor you have to provide a file named ``componentregistry.xml`` in your
profile directory, which looks similar to this.:
  
  <?xml version="1.0"?>
  <componentregistry>
  
    <utilities>
    
      <utility
        name="mysoup"
        factory="mymodule.MySoup"
        interface="cornerstone.soup.interfaces.ISoup"
      />
    
      <utility
        name="mysoup"
        factory="five.intid.intid.OFSIntIds"
        interface="zope.app.intid.interfaces.IIntIds"
      />
    
    </utilities>
  
  </componentregistry>

After including cornerstone.soup and your module in your instance and after
applying the GS profile, you can query the soup utility.:

  >>> from zope.component import getUtility
  >>> from cornerstone.soup.interfaces import ISoup
  >>> soup = getUtility(ISoup, name=u'mysoup')

A Soup can only contain ``Records``. A Record is a simple persistent object
which accepts any keyword arguments on ``__init__`` time. This arguments are 
used as Record properties. Be aware that the rules to persist to the ZODB
applies here.:

  >>> from cornerstone.soup import Recordecord(name
  
  >>> rec = Record(name=u'rec1')
  >>> soup.add(rec)
  >>> rec = Record(name=u'rec2')
  >>> soup.add(rec)
  
  >>> soup.query(name=u'rec1')
  [<Record at /.../record-0>]
  
  >>> soup.query(name=u'rec2')
  [<Record at /.../record-1>]

If you modify a record already contained inside the soup, and an attribute which
is used to catalog the record is modified, you have to reindex this record.:

  >>> rec.name = u'rec1'
  >>> soup.reindex([rec])
  >>> soup.query(name=u'rec1')
  [<Record at /.../record-0>, <Record at /.../record-1>]
  
You can rebuild the whole catalog as well.:

  >>> soup.rebuild()
  
Deleting records from the soup is implemented via the ``__delitem__`` function.:

  >>> del soup[rec]
  >>> soup.query(name=u'rec1')
  [<Record at /.../record-0>]

TODO
====

  * fix the tests. I have to take a closer look on how to setup a test ZODB and
    an appropriate local component registry to make the soup work properly
    inside the test environment.

Changes
=======

  * 1.0b1 (rnix, jensens) - initial work

Contributors
============

  * Robert Niederreiter <rnix@squarewave.at>
  * Jens Klein <jens@bluedynamics.com>