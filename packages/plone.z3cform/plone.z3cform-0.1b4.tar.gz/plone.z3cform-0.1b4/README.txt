plone.z3cform
=============

plone.z3cform is a library that allows use of z3c.form with Zope 2 and
Plone.

More documentation to come.  For now, please refer to the
``collective.dancing`` package for examples of use.

Uberselection widget
--------------------

This package provides a query source compatible with
``z3c.formwidget.query`` which combines to an uberselection widget for
the ``z3c.form`` form generation framework.

The native value type for the widget is Archetypes UID collections.

Example:

  >>> from plone.z3cform.uberselect import \
  ...     ArchetypesContentSourceBinder
  
  >>> class ISelection(interface.Interface):
  ...     items = schema.Set(
  ...         title=u"Selection",
  ...         description=u"Search for content.",
  ...         value_type=schema.Choice(
  ...             source=ArchetypesContentSourceBinder()
  ...         )
  ...     )

A recipe to store references as ``persistent.wref.WeakRef`` instead of
UID is to use the ``uid2wref`` adapter between the form and the
context.

  >>> from plone.z3cform.uberselect import uid2wref
  
  >>> Factory = uid2wref(ISelection['items'])

To store weak references instead of UIDs you would register such a
factory as a component adapting the context. The factory automatically
provides the interface which defines the field.
