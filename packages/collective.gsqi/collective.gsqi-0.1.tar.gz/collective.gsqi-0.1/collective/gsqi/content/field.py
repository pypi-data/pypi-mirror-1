from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class FieldsStructureAdapter(content.StructureFolderWalkingAdapter,
                             common.PropertiesStructureAdapter):
    """Set Archetypes fields"""

    def _makeInstance(self, id, portal_type, subdir, import_context):
        """Set Archetypes fields"""
        content = super(FieldsStructureAdapter, self)._makeInstance(
            id, portal_type, subdir, import_context)

        parser = self._getPropsParser(id, subdir, import_context)
        if parser is not None and parser.has_section('FIELDS'):
            defaults = dict(parser.items('DEFAULT'))
            kwargs = {}
            for key, value in parser.items('FIELDS'):
                if key not in defaults:
                    if content.getField(key).multiValued:
                        kwargs[key] = [line.strip() for line in
                                        value.split('\n')]
                    else:
                        kwargs[key] = value
            content.update(**kwargs)

        return content
