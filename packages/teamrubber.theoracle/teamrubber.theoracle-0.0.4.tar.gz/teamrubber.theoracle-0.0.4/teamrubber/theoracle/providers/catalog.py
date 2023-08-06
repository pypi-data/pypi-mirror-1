from teamrubber.theoracle.base_provider import BaseProvider
from teamrubber.theoracle.infofragment import InfoFragment
from Products.CMFCore.utils import getToolByName


class CatalogBase(object):

    indexes = {}
    metadata = {}

    def update(self):
        rid = None
        try:
            catalog = getToolByName(self.context,'portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            results = catalog.searchResults(path=path,getId=self.context.id,sort_on='created',sort_order='reverse')

            if len(results) > 0:
                rid = results[0].getRID()
            
            if rid:
                self.indexes = catalog.getIndexDataForRID(rid)
                self.metadata = catalog.getMetadataForRID(rid)
        except:
            pass
        

class CatalogIndexes(CatalogBase,BaseProvider):
    template = 'CatalogIndexes.pt'
    
    def getCatalogIndexes(self):
        return InfoFragment(self.indexes)


class CatalogMetadata(CatalogBase,BaseProvider):
    template = 'CatalogMetadata.pt'
    
    def getCatalogMetadata(self):
        return InfoFragment(self.metadata)
