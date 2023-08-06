from zope.interface import implements

from zope.catalog.catalog import Catalog
from zope.catalog.field import FieldIndex

from cornerstone.soup.interfaces import ICatalogFactory
from cornerstone.soup import Soup

class MySoup(Soup):
    id = u'mysoup'

class MyCatalogFactory(object):
    """ICatalogFactory implementation used for testing.
    """

    implements(ICatalogFactory)

    def __call__(self):
        catalog = Catalog()
        catalog[u'user'] = FieldIndex(field_name='user',
                                      field_callable=False)
        return catalog