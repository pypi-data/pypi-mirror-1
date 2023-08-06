.. -*-doctest-*-

=============
Import groups
=============

Before we run the import step, the site has only the default groups.

    >>> portal.acl_users.getGroupById('foo_group_id')
    >>> portal.acl_users.getGroupById('bar_group_id')

Write the XML to be imported.

    >>> xml = """
    ... <groups xmlns="http://namespaces.zope.org/gsml">
    ...   <group id="foo_group_id"
    ...          title="Foo Group Title"
    ...          description="Foo Group Description"
    ...          email="foo@foo.com" />
    ...   <group xmlns="http://namespaces.zope.org/gsml"
    ...          id="bar_group_id" />
    ... </groups>"""

Run the GenericSetup import step with a context that has access to the
XML.

    >>> from Products.GenericSetup import context
    >>> context_ = context.DirectoryImportContext(
    ...     portal.portal_setup, '')
    >>> context_.readDataFile = lambda *args, **kw: xml
    >>> portal.portal_setup._doRunImportStep(
    ...     'groups', context_)

The site now reflects the import.

    >>> group = portal.acl_users.getGroupById('foo_group_id')
    >>> group.getProperties()
    {'email': u'foo@foo.com', 'description': u'Foo Group Description',
    'title': u'Foo Group Title'}

    >>> group = portal.acl_users.getGroupById('bar_group_id')
    >>> group.getProperties()
    {'email': '', 'description': '', 'title': ''}
