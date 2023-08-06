from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class LocalRoleStructureAdapter(
    content.StructureFolderWalkingAdapter,
    common.PropertiesStructureAdapter):
    """Perform workflow transitions"""

    def _makeInstance(self, id, portal_type, subdir, import_context):
        """Perform workflow transitions"""
        content = super(LocalRoleStructureAdapter, self)._makeInstance(
            id, portal_type, subdir, import_context)

        parser = self._getPropsParser(id, subdir, import_context)
        if parser is not None and parser.has_section('ROLES'):
            defaults = dict(parser.items('DEFAULT'))
            for user_id, roles in parser.items('ROLES'):
                if user_id not in defaults:
                    roles = [role.strip() for role in roles.split()
                             if role.strip()]
                    content.manage_setLocalRoles(user_id, roles)

        return content
