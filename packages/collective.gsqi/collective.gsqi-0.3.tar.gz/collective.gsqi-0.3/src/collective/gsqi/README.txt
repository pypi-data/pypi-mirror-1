.. -*-doctest-*-

===============
collective.gsqi
===============

This package is my grab bag of patches to GS and portal_quickinstaller
I use in my client work.  It is unstable, unpolished, subject to my
whim, and really should be experimental.gsqi.  If, however, the same
GenericSetup and portal_quickinstaller quirks and bugs bother you, or
the same conveniences are of value to you, you might want to look at
whats in it.
       
  - Fix `import of group roles
    <http://dev.plone.org/collective/browser/collective.gsqi/trunk/collective/gsqi/workflow/exportimport.py>`_
    during workflow import

  - Fix `circular import handler dependencies
    <http://dev.plone.org/plone/ticket/8350>`_ bug

  - Fix portal_quickinstaller so that `persistent data is not lost
    <http://dev.plone.org/collective/browser/collective.gsqi/trunk/collective/gsqi/qi.py>`_
    on reinstall

Also included are a number of perhaps naughty extensions to the CMF
content import handler.

  - Permissive registrations of the StructureFolderWalkingAdapter so
    that folders under the profile's "structure" folder with the same
    name as in the container's .objects file can be used to import any
    kind of content object, not just folders.  This allows, amongst
    other things, creating topics/collections and criteria on import.

  - Set arbitrary AT fields on import using the options under the
    [FIELDS] section of .properties as field names and the option
    values as field values.  If field.multiValued is True, then the
    option value will be split on newlines and each value stripped.

  - Reindex imported objects so that imported titles, descriptions,
    and any other AT fields are reflected in the catalog and portal
    navigation after import.

  - Set local roles on import where each option under the [ROLES]
    section of .properties is the principal/user id and the roles
    assigned to that principal are taken from the option value split
    at newlines with each item stripped.

  - Do each workflow transition listed under the "transitions" option
    of the [DEFAULT] section of .properties.  The option value is
    split at newlines with each item stripped.

  - Set display layout using the layout option in the [DEFAULT]
    section of .properties

Here's a sample .properties file demonstrating all these extensions::

    [DEFAULT]
    title = News and Events
    description = Site News and Events
    transitions = publish
    layout = aggregator
    
    [ROLES]
    Marketers = Contributor
    
    [FIELDS]
    excludeFromNav = True
    constrainTypesMode = 1
    locallyAllowedTypes =
        Event
        News Iem
    immediatelyAddableTypes =
        Event
        News Iem

Also included is `GSML <http://rpatterson.net/blog/gsml>`_ which
allows implementing GS import handlers as you would implement ZCML
directive handlers.  Some import handlers are included in
collective.gsqi that make use of GSML.

  - A `groups import handler
    <http://dev.plone.org/collective/browser/collective.gsqi/trunk/collective/gsqi/group/README.txt>`_

  - A `references import handler
    <http://dev.plone.org/collective/browser/collective.gsqi/trunk/collective/gsqi/refs/meta.py>`_
