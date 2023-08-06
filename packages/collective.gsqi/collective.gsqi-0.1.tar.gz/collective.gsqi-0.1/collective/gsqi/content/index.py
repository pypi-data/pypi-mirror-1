from Products.CMFCore.exportimport import content

class IndexingStructureAdapter(content.StructureFolderWalkingAdapter):
    """Catalog changed indexes"""

    def _makeInstance(self, *args, **kw):
        """Catalog changed indexes"""
        content = super(IndexingStructureAdapter, self)._makeInstance(
            *args, **kw)
        content.reindexObject(
            idxs=['Title', 'sortable_title', 'Description'])
        return content
