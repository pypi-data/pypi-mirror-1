from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class LocalRoleStructureAdapter(
    content.StructureFolderWalkingAdapter,
    common.PropertiesStructureAdapter):
    """Perform workflow transitions"""

    def import_(self, import_context, subdir, root=False):
        """Perform workflow transitions"""
        parser = self._getPropsParser(
            self.context.getId(), subdir, import_context)
        if parser is not None and parser.has_section('ROLES'):
            defaults = dict(parser.items('DEFAULT'))
            for user_id, roles in parser.items('ROLES'):
                if user_id not in defaults:
                    roles = [role.strip() for role in roles.split()
                             if role.strip()]
                    self.context.manage_setLocalRoles(user_id, roles)

        return super(LocalRoleStructureAdapter, self).import_(
            import_context, subdir, root=root)
