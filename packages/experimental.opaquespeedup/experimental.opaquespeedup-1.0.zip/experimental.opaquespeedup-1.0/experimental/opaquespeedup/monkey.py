from Acquisition import aq_base
from Products.CMFCore.interfaces.IOpaqueItems import ICallableOpaqueItem
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.utils import getToolByName


def fqin(interface):
    """ fully qualified interface name """
    return '%s.%s' % (interface.__module__, interface.__name__)


def opaqueItems(self):
    """ return opaque items (subelements that are contained
        using something that is not an ObjectManager) """
    base = aq_base(self)
    ids = getattr(base, '_v_opaque_ids', None)
    if ids is None:
        # fall back if there is no catalog
        catalog = getToolByName(self, 'portal_catalog', None)
        if catalog is None:
            return self.originalOpaqueItems()
        # first look up all opaque items using the catalog
        path = '/'.join(self.getPhysicalPath())
        query = dict(object_provides=fqin(ICallableOpaqueItem),
                     path=dict(query=path, depth=1))
        brains = catalog.unrestrictedSearchResults(query)
        ids = [ b.getId for b in brains ]
        # also add talkback if it exists (see CMFCatalogAware.py)
        if hasattr(base, 'talkback'):
            talkback = base.talkback
            if talkback is not None:
                ids.append(talkback.id)
        base._v_opaque_ids = ids
    return tuple([ (i, getattr(base, i)) for i in ids ])


def applyPatch():
    """ apply the monkey patch """
    CMFCatalogAware.originalOpaqueItems = CMFCatalogAware.opaqueItems
    CMFCatalogAware.opaqueItems = opaqueItems

