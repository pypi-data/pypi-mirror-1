Overview
========

``cornerstone.soup`` provides a container for persistent records which are
queryable. The code is tested with Plone3.3 but should work with any Zope2.10+
application, as long as the appropriate utility is provided as persistent
local component.


Usage
=====

Subclass the ``Soup`` object and give it an appropriate id
::

  >>> from cornerstone.soup import Soup
  >>> class MySoup(Soup):
  ...     id = u'mysoup'


We have to provide an ``ICatalogFactory`` implementation for our soup
::

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



Now, these 2 objects must be registered under the same name as the id of the 
soup. Register the ``ICatalogFactory`` as utility via ZCML
::

  <utility
    name="mysoup"
    factory=".mymodule.MyCatalogFactory"
    provides="cornerstone.soup.interfaces.ICatalogFactory"
  />


The ``ISoup`` utility is registered as a local component.
  
In Plone you can easily register you local components via GenericSetup.
Therefor you have to provide a file named ``componentregistry.xml`` in your
profile directory, which looks similar to this
::
  
 <utilities>  
   <utility
     name="mysoup"
     factory="mymodule.MySoup"
     interface="cornerstone.soup.interfaces.ISoup"
   />    
 </utilities>


After including ``cornerstone.soup`` and your module in your instance and after
applying the GS profile, you can query the soup utility
::

  >>> from zope.component import getUtility
  >>> from cornerstone.soup.interfaces import ISoup
  >>> soup = getUtility(ISoup, name=u'mysoup')


A Soup can only contain ``Records``. A Record is a simple persistent object
which accepts any keyword arguments on ``__init__`` time. This arguments are 
used as Record properties. Be aware that the rules to persist to the ZODB
applies here.

Create a Record and add it to soup
::

    >>> from cornerstone.soup import Record
    >>> record = Record(user='user1')
    >>> id = soup.add(record)

Check querying
::

    >>> [r for r in soup.query(user='user1')]
    [<Record at ...>]
    
    >>> [r for r in soup.query(user='nonexist')]
    []
    
Add some more Records
::

    >>> id = soup.add(Record(user='user1'))
    >>> id = soup.add(Record(user='user2'))
    >>> u1records = [r for r in soup.query(user='user1')]
    >>> u1records
    [<Record at ...>, 
    <Record at ...>]

Change user attribute of one record
::

    >>> u1records[0].data['user'] = 'user2'

The query still returns the old result. The Record must be reindexed
::

    >>> [r for r in soup.query(user='user1')]
    [<Record at ...>, 
    <Record at ...>]
    
    >>> soup.reindex([u1records[0]])
    
    >>> u1 = [r for r in soup.query(user='user1')]
    >>> u1
    [<Record at ...>]
    
    >>> u2 = [r for r in soup.query(user='user2')]
    >>> u2
    [<Record at ...>, 
    <Record at ...>]

You can reindex all records in soup at once
::

    >>> all = [r for r in soup.data.values()]
    >>> all = sorted(all, key=lambda x: x.user)
    >>> all
    [<Record at ...>, 
    <Record at ...>, 
    <Record at ...>]
    
    >>> all[-1].data['user'] = 'user3'
    >>> soup.reindex()
    >>> [r for r in soup.query(user='user3')]
    [<Record at ...>]

You can also rebuild the catalog. In this case the catalog factory is called
again and the new catalog is used. Lets modify catalog of catalog factory
::

    >>> from zope.catalog.field import FieldIndex
    >>> catalogfactory = getUtility(ICatalogFactory, name='mysoup')
    >>> catalogfactory.catalog[u'name'] = FieldIndex(field_name='name',
    ...                                   field_callable=False)
    >>> catalogfactory()[u'name']
    <zope.catalog.field.FieldIndex object at ...>

Set name attribute on some record data, rebuild soup and check results
::

    >>> all[0].data['name'] = 'name'
    >>> all[1].data['name'] = 'name'
    >>> all[2].data['name'] = 'name'
    >>> soup.rebuild()
    >>> [r for r in soup.query(name='name')]
    [<Record at ...>, 
    <Record at ...>, 
    <Record at ...>]
    

We can delete items as well *hurrey*
::

    >>> del soup[all[0]]
    >>> [r for r in soup.query(name='name')]
    [<Record at ...>, 
    <Record at ...>]

For huge expected results we can query LazyRecords. They return the real record
on call
::

    >>> lazy = [l for l in soup.lazy(name='name')]
    >>> lazy
    [<cornerstone.soup.soup.LazyRecord object at ...>, 
    <cornerstone.soup.soup.LazyRecord object at ...>]
    
    >>> lazy[0]()
    <Record at ...>


Changes
=======


  * 1.0
    - complete tests 2009-12-02 - rnix
    - remove IIntIds and INameChooser dependencies 2009-12-02 - rnix, jensens

  * 1.0b2
    - change namechoosing of records. Use ``uuid.uuid4()`` 2009-10-01 - rnix
    - add ``lazy`` function for querying huge results 2009-10-01 - rnix
    - yield query result instead of collect in a list 2009-09-29 - rnix

  * 1.0b1
    - initial work - rnix, jensens


Contributors
============

  * Robert Niederreiter <rnix@squarewave.at>
  * Jens Klein <jens@bluedynamics.com>
