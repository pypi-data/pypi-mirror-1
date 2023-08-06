from zope import interface
from zope import schema

from zope.configuration import config

class IGroupsDirective(interface.Interface):
    pass

class IGroupDirective(interface.Interface):

    id = schema.ASCIILine(title=u'Id')

IGroupDirective.setTaggedValue('keyword_arguments', True)

class Groups(config.GroupingContextDecorator):
    pass

def importGroup(_context, id, **kw):
    import_context = _context.context.import_context
    tool = import_context.getSite().portal_groups

    group = tool.getGroupById(id)
    if group is not None and import_context.shouldPurge():
        _context.action(discriminator=('removeGroup', id),
                        callable=tool.removeGroup, args=(id,))
        
    _context.action(discriminator=('addGroup', id),
                    callable=tool.addGroup, args=(id, (), (), kw))
