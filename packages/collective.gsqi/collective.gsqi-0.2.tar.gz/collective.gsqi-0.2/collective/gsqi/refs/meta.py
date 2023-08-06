from zope import interface
from zope import schema

from zope.configuration import config

class IReferencesDirective(interface.Interface):
    pass

class ISourceDirective(interface.Interface):

    path = schema.ASCIILine(title=u'Source Path')

class IRelationshipDirective(interface.Interface):

    name = schema.TextLine(
        title=u'Relationship Name', required=False)

class ITargetDirective(interface.Interface):

    path = schema.ASCIILine(title=u'Target Path')

class Path(config.GroupingContextDecorator):

    def __init__(self, context, path):
        super(Path, self).__init__(context)
        self.path = path

    def before(self):
        self.obj = self.context.import_context.getSite(
            ).restrictedTraverse(self.path)
 
def target(_context, path):
    target_obj = _context.import_context.getSite(
        ).restrictedTraverse(path)
    source = _context.context.context
    relationship=_context.context.name
    _context.action(
        discriminator=('addReference', source.path,
                       relationship, path),
        callable=source.obj.addReference,
        args=(target_obj,), kw=dict(relationship=relationship))
