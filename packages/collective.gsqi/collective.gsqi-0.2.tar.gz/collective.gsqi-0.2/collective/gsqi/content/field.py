from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class FieldsStructureAdapter(content.StructureFolderWalkingAdapter,
                             common.PropertiesStructureAdapter):
    """Set Archetypes fields"""

    def import_(self, import_context, subdir, root=False):
        """Set Archetypes fields"""

        parser = self._getPropsParser(
            self.context.getId(), subdir, import_context)
        if parser is not None and parser.has_section('FIELDS'):
            defaults = dict(parser.items('DEFAULT'))
            kwargs = {}
            for key, value in parser.items('FIELDS'):
                if key not in defaults:
                    if self.context.getField(key).multiValued:
                        kwargs[key] = [line.strip() for line in
                                        value.split('\n')]
                    else:
                        kwargs[key] = value
            self.context.update(**kwargs)

        return super(FieldsStructureAdapter, self).import_(
            import_context, subdir, root=root)
