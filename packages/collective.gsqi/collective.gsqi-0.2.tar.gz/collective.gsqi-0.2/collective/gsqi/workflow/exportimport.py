from Products.DCWorkflow import exportimport

class DCWorkflowDefinitionBodyAdapter(
    exportimport.DCWorkflowDefinitionBodyAdapter):
    """Fix group import"""

    def _importBody(self, body):
        """Fix group import"""
        super(DCWorkflowDefinitionBodyAdapter, self)._importBody(body)
        for state in self.context.states.objectValues():
            map(state.addGroup, state.group_roles)

    body = property(
        exportimport.DCWorkflowDefinitionBodyAdapter._exportBody,
        _importBody)
