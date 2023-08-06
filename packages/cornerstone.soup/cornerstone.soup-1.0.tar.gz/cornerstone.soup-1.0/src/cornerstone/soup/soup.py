# Copyright 2003-2009, BlueDynamics Alliance - http://bluedynamics.com

import uuid
import random

from zope.interface import implements
from zope.component import getUtility
from zope.location import Location

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem

from interfaces import ISoup
from interfaces import IRecord
from interfaces import ICatalogFactory

class Soup(SimpleItem, Location):
    """ISoup implementation.
    
    Abstract. This class is supposed to be derived from.
    """
    implements(ISoup)
    
    id = None
    
    def __init__(self, *args, **kw):
        SimpleItem.__init__(self, *args, **kw)
        Location.__init__(self, *args, **kw)
        self.data = IOBTree()
    
    @property
    def catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = getUtility(ICatalogFactory, name=self.id)()
        return self._catalog

    def add(self, record):
        record.__parent__ = self
        record.intid = self._generateid()
        self.data[record.intid] = record
        record = self.data[record.intid] #?
        self.catalog.index_doc(record.intid, record)
        # XXX: notify subscribers here if not done by OFS, check this.
        return record.intid
    
    def _query(self, **kw):
        querykw = {}
        for key in kw:
            if isinstance(kw[key], list) \
              or isinstance(kw[key], tuple):
                assert(len(kw[key]) == 2)
                querykw[key] = kw[key]
            else:
                querykw[key] = (kw[key], kw[key])
        return self.catalog.apply(querykw)
    
    def query(self, **kw):
        ids = self._query(**kw)
        for id in ids:
            yield self.data[id]
    
    def lazy(self, **kw):
        ids = self._query(**kw)
        for id in ids:
            yield LazyRecord(id, self)
    
    def rebuild(self):
        self._catalog = getUtility(ICatalogFactory, name=self.id)()
        self.reindex()
    
    def reindex(self, records=None):
        if records is None:
            records = self.data.values()
        for record in records:
            self.catalog.index_doc(record.intid, record)

    def __delitem__(self, record):
        if not record.__parent__.id == self.id:
            raise ValueError(u"Record not contained in this soup")
        del self.data[record.intid]
        self.catalog.unindex_doc(record.intid)
    
    _v_nextid = None   
    _randrange = random.randrange
    
    def _generateid(self):
        """Stolen from zope.app.intid.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.data:
                return uid
            self._v_nextid = None

class LazyRecord(object):
    """Object for fetching the real record.
    """
    
    def __init__(self, intid, soup):
        self.intid = intid
        self.soup = soup
    
    def __call__(self):
        return self.soup.data[self.intid]

EMPTY_MARKER = object()

class Record(SimpleItem, Location):
    """IRecord implementation.
    """
    implements(IRecord)
    
    def __init__(self, **kw):
        self.id = uuid.uuid4().hex
        self.intid = None
        self.data = OOBTree()
        for key in kw.keys():
            self.data[key] = kw[key]
        self._p_changed = True
    
    def __getattribute__(self, name):
        try:
            attr = SimpleItem.__getattribute__(self, 'data').get(name,
                                                                 EMPTY_MARKER)
            if attr is not EMPTY_MARKER:
                return attr
        except AttributeError, e: pass
        return SimpleItem.__getattribute__(self, name)