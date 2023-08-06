.. -*-doctest-*-

===========================================
GenericSecup handlers using the ZCML engine
===========================================

Start with a callable that should be called as a result of running the
import step with arguments marshalled from the GSML.

    >>> from collective.gsqi.gsml import testing
    >>> testing.setFoo
    <function setFoo at ...>

Define a directive schema.

    >>> testing.IFooDirective
    <InterfaceClass collective.gsqi.gsml.testing.IFooDirective>

Define the handler as you would with a ZCML handler.  The context is
an extended ZCML context that supports the same action registration
and conflict reconciliation as ZCML contexts.  The root ZCML
configuration machine also has a generic setup context as the
'import_context' attribute and can return the site as in
"_context.context.import_context.getSite()".

    >>> testing.ImportFoo
    <class 'collective.gsqi.gsml.testing.ImportFoo'>

Register the handler as a special GenericSetup import step handler.

    >>> from Products.Five import zcml
    >>> zcml.load_string("""
    ... <configure
    ...     xmlns="http://namespaces.zope.org/zope"
    ...     xmlns:meta="http://namespaces.zope.org/meta"
    ...     xmlns:gsml="http://namespaces.zope.org/gsml">
    ...   <gsml:importStep
    ...      namespace="http://namespaces.zope.org/gsml"
    ...      name="foo"
    ...      title="Import Foo"
    ...      description="Set the site foo attribute."
    ...      schema="collective.gsqi.gsml.testing.IFooDirective"
    ...      handler="collective.gsqi.gsml.testing.ImportFoo" />
    ... </configure>""")

Before we run the import step, the site does not reflect the import.

    >>> hasattr(portal, 'foo')
    False

Write the XML to be imported.

    >>> xml = """<foo xmlns="http://namespaces.zope.org/gsml"
    ...               value="bar" />"""

Run the GenericSetup import step with a context that has access to the
XML.

    >>> from Products.GenericSetup import context
    >>> context_ = context.DirectoryImportContext(
    ...     portal.portal_setup, '')
    >>> context_.readDataFile = lambda *args, **kw: xml
    >>> portal.portal_setup._doRunImportStep(
    ...     'foo', context_)

The site now reflects the import.

    >>> portal.foo
    u'bar'

The handler doesn't do anything if the file isn't present in the
profile.

    >>> context_.readDataFile = lambda *args, **kw: None
    >>> portal.portal_setup._doRunImportStep(
    ...     'foo', context_)

    >>> portal.foo
    u'bar'
