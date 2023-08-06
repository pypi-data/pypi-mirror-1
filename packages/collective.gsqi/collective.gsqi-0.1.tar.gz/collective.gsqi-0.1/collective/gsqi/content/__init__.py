from collective.gsqi.content import index
from collective.gsqi.content import field
from collective.gsqi.content import role
from collective.gsqi.content import workflow

class StructureFolderWalkingAdapter(
    index.IndexingStructureAdapter, field.FieldsStructureAdapter,
    role.LocalRoleStructureAdapter,
    workflow.TransitionStructureAdapter):
    pass
