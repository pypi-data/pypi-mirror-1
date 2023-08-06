from zope import interface
from zope import schema

from zope.configuration import config

class IFooDirective(interface.Interface):
    value = schema.TextLine(title=u'Value')

def setFoo(site, value):
    site.foo = value

class ImportFoo(config.GroupingContextDecorator):

    def __init___(self, context, value):
        super(ImportFoo, self).__init__(context)
        self.value = value

    def after(self):
        self.context.action(
            discriminator=('foo', self.value), callable=setFoo,
            args=(self.context.import_context.getSite(), self.value))
        
