from Products.CMFCore.exportimport import content

from collective.gsqi.content import common

class TransitionStructureAdapter(
    content.StructureFolderWalkingAdapter,
    common.PropertiesStructureAdapter):
    """Perform workflow transitions"""

    def import_(self, import_context, subdir, root=False):
        """Perform workflow transitions"""
        site = import_context.getSite()

        parser = self._getPropsParser(
            self.context.getId(), subdir, import_context,
            defaults={'transitions': ''})
        if parser is not None:
            transitions = (
                t.strip() for t in
                parser.get('DEFAULT', 'transitions').split()
                if t.strip())
            for transition in transitions:
                for wf in site.portal_workflow.getWorkflowsFor(
                    self.context):
                    if wf.isActionSupported(self.context, transition):
                        site.portal_workflow.doActionFor(
                            self.context, transition)
                        break

        return super(TransitionStructureAdapter, self).import_(
            import_context, subdir, root=root)
