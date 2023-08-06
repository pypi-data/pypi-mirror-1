from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class TransitionStructureAdapter(
    content.StructureFolderWalkingAdapter,
    common.PropertiesStructureAdapter):
    """Perform workflow transitions"""

    def _makeInstance(self, id, portal_type, subdir, import_context):
        """Perform workflow transitions"""
        content = super(TransitionStructureAdapter, self)._makeInstance(
            id, portal_type, subdir, import_context)
        site = import_context.getSite()

        parser = self._getPropsParser(
            id, subdir, import_context, defaults={'transitions': ''})
        if parser is not None:
            transitions = (
                t.strip() for t in
                parser.get('DEFAULT', 'transitions').split()
                if t.strip())
            for transition in transitions:
                site.portal_workflow.doActionFor(content, transition)

        return content
