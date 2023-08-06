import transaction

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from zope.location import Location
from zope.app.intid.interfaces import IIntIds
from zope.container.interfaces import INameChooser
from zope.keyreference.interfaces import IKeyReference, NotYet

from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2

from interfaces import ISoup
from interfaces import IRecord
from interfaces import ICatalogFactory

class KeyReferenceToRecord(object):
    """IKeyReference implementation referencing Records inside a Soup.
    """
    implements(IKeyReference)
    adapts(IRecord)
    
    key_type_id = 'cornerstone.soup.keyreference'
    
    def __init__(self, wrapped_obj):
        if not wrapped_obj.id:
            raise NotYet()
        self.soupid = wrapped_obj.__parent__.id
        self.refid = wrapped_obj.id
    
    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            self._storage = getUtility(ISoup, name=self.soupid)
        return self._storage
    
    def __call__(self):
        return self.storage.get(self.refid, None)

    def __hash__(self):
        return hash((self.soupid, self.storage, self.refid))

    def __cmp__(self, other):
        if self.key_type_id == other.key_type_id:
            myident = '%s.%s' % (self.soupid, self.refid)
            otherident = '%s.%s' % (other.soupid, other.refid)
            return cmp(myident, otherident)
        # XXX: check wether below comparsion is even
        return cmp(self.key_type_id, other.key_type_id)

class NameChooser(object):
    """INameChooser implementation for records.
    """
    implements(INameChooser)
    
    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        if not name == 'record':
            raise ValueError(u"Odd name given")

    def chooseName(self, name, object):
        self.checkName(name, object)
        name = '%s-%i' % (name, self.context.nextrecordindex)
        self.context.nextrecordindex += 1
        return name

class Soup(BTreeFolder2, Location):
    """ISoup implementation.
    
    Abstract. This class is supposed to be derived from.
    """
    implements(ISoup)
    
    id = None
    
    def __init__(self, *args, **kw):
        BTreeFolder2.__init__(self, *args, **kw)
        self.nextrecordindex = 0
    
    @property
    def catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = getUtility(ICatalogFactory, name=self.id)()
        return self._catalog

    def add(self, record):
        nc = INameChooser(self)
        id = nc.chooseName('record', record)
        record.id = id
        record.__parent__ = self
        self[id] = record
        record = self[id]
        intids = getUtility(IIntIds, name=self.id)
        record.intid = intids.register(record)
        self.catalog.index_doc(record.intid, record)
        # XXX: notify subscribers here
        return record.intid
                    
    def query(self, **kw):
        querykw = {}
        for key in kw:
            if isinstance(kw[key], list) \
              or isinstance(kw[key], tuple):
                assert(len(kw[key]) == 2)
                querykw[key] = kw[key]
            else:
                querykw[key] = (kw[key], kw[key])
        ids = self.catalog.apply(querykw)
        intids = getUtility(IIntIds, name=self.id)
        result = list()
        for id in ids:
            record = intids.getObject(id)
            result.append(record)
        return result
    
    def rebuild(self):
        self._catalog = getUtility(ICatalogFactory, name=self.id)()
        self.reindex()
    
    def reindex(self, records=None):
        if records is None:
            records = self.objectValues()
        for record in records:
            if record.intid is None:
                intids = getUtility(IIntIds, name=self.id)   
                intids.unregister(record) # paranoid
                record.intid = intids.register(record)
            self.catalog.index_doc(record.intid, record)

    def __delitem__(self, record):
        if not record.__parent__.id == self.id:
            raise ValueError(u"Record not contained in this soup")
        BTreeFolder2.__delitem__(self, record.id)
        self.catalog.unindex_doc(record.intid)

EMPTY_MARKER = object()

class Record(SimpleItem, Location):
    """IRecord implementation.
    """
    implements(IRecord)
    
    def __init__(self, **kw):
        self.id = None
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