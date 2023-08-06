from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class LayoutStructureAdapter(
    content.StructureFolderWalkingAdapter,
    common.PropertiesStructureAdapter):
    """Chang content layouts"""

    def import_(self, import_context, subdir, root=False):
        """Perform workflow layouts"""
        site = import_context.getSite()

        parser = self._getPropsParser(
            self.context.getId(), subdir, import_context,
            defaults={'layout': ''})
        if parser is not None:
            layout = parser.get('DEFAULT', 'layout').strip()
            if layout:
                self.context.setLayout(layout)

        return super(LayoutStructureAdapter, self).import_(
            import_context, subdir, root=root)
