from persistent import Persistent
from zope.interface import implements
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
from collective.indexing.interfaces import IIndexQueueProcessor


# container to hold references to the original indexing methods
# these are populated by `collective.indexing.monkey`
catalogMultiplexMethods = {}
catalogAwareMethods = {}


def getDispatcher(obj, name):
    """ return named indexing method according on the used mixin class """
    if isinstance(obj, CatalogMultiplex):
        op = catalogMultiplexMethods.get(name, None)
    elif isinstance(obj, CMFCatalogAware):
        op = catalogAwareMethods.get(name, None)
    else:
        op = None
    return op


class IPortalCatalogQueueProcessor(IIndexQueueProcessor):
    """ an index queue processor for the standard portal catalog via
        the `CatalogMultiplex` and `CMFCatalogAware` mixin classes """


class PortalCatalogQueueProcessor(Persistent):
    implements(IPortalCatalogQueueProcessor)

    def index(self, obj, attributes=None):
        op = getDispatcher(obj, 'index')
        if op is not None:
            op(obj)

    def reindex(self, obj, attributes=None):
        op = getDispatcher(obj, 'reindex')
        if op is not None:
            op(obj, attributes or [])

    def unindex(self, obj):
        op = getDispatcher(obj, 'unindex')
        if op is not None:
            op(obj)

    def begin(self):
        pass

    def commit(self):
        pass

