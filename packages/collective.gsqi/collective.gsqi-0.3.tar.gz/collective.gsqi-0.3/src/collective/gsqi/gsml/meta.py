from zope.configuration import interfaces
from zope.configuration import config
from zope.configuration import xmlconfig

from Products.GenericSetup import zcml
from Products.GenericSetup import registry
from Products.GenericSetup import utils

class IImportStepDirective(config.IStandaloneDirectiveInfo,
                           zcml.IImportStepDirective):
    """Stitch together the GenericSetup and ZCML directives"""

class ImportStep(zcml.importStep, object):
    
    def __init__(
        self, context, name, title, description, schema, handler,
        namespace='', usedIn=interfaces.IConfigurationContext):
        super(ImportStep, self).__init__(
            context, name, title, description, handler)
        self.schema = schema
        self.namespace = namespace
        self.usedIn = usedIn

    def __call__(self):
        config.defineGroupingDirective(
            self.context, self.name, self.schema, self.handler,
            self.namespace, self.usedIn)

        self.handler.include = self.include
        handler_dotted = '.'.join(
            [utils._getDottedName(self.handler), 'include'])
        zcml._import_step_regs.append(self.name)
        self.context.action(
            discriminator=self.discriminator,
            callable=registry._import_step_registry.registerStep,
            args=(self.name, None, handler_dotted, self.dependencies,
                  self.title, self.description))

    def include(self, import_context):
        context = self.getRootContext()
        context.import_context = import_context
        
        filename = self.name+'.xml'
        xml = import_context.readDataFile(filename)
        if xml is not None:
            xmlconfig.string(xml, context=context, name=filename)

        del context.import_context

    def getRootContext(self):
        context = self.context
        while hasattr(context, 'context'):
            context = context.context
        return context
