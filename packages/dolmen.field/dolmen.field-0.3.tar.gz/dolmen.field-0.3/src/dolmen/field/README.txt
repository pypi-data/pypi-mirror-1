============
dolmen.field
============

The `dolmen.field` package provides additional generic fields to
extend `zope.schema`.


Configuration fields
====================

The configuration fields are used for description and constraints, to
impose a consistent schema and data model.

GlobalClass
-----------

`GlobalClass` is a field requiring a valid Interface class. It can be
used for factories and other components that need to store an
interface with the possibility to check and verify the consistency of
the given value::

  >>> from zope.interface import Interface
  >>> from dolmen.field import GlobalClass, IClassField

  >>> class IDummy(Interface):
  ...     def shall_fail():
  ...         pass

  >>> class Dummy(object):
  ...     pass

Of course, it must be a valid interface::

  >>> field = GlobalClass(
  ...             title=u'a class field',
  ...             schema=object
  ...             )
  Traceback (most recent call last):
  ...
  WrongType: <type 'object'> is not a valid Interface

The interface will be used to validate the class::
   
  >>> field = GlobalClass(
  ...             title=u'a class field',
  ...             schema=IDummy
  ...             )

  >>> field.schema
  <InterfaceClass dolmen.field.tests.IDummy>
  >>> IClassField.providedBy(field)
  True

We make sure the `interface` attribute is not touched::
   
  >>> print field.interface
  None

In a first time, we make sure the class implements the needed interface::

  >>> field._validate(Dummy)
  Traceback (most recent call last):
  ...
  ConstraintNotSatisfied: <class 'dolmen.field.tests.Dummy'> does not implement <InterfaceClass dolmen.field.tests.IDummy>
  
  >>> from zope.interface import classImplements
  >>> classImplements(Dummy, IDummy)
  >>> IDummy.implementedBy(Dummy)
  True

Then the interface acts as a strict validator::

  >>> field._validate(Dummy)
  Traceback (most recent call last):
  ...
  BrokenImplementation: An object has failed to implement interface <InterfaceClass dolmen.field.tests.IDummy>
  <BLANKLINE>
  The shall_fail attribute was not provided.
  <BLANKLINE>

  >>> Dummy.shall_fail = lambda x: u'not'
  >>> field._validate(Dummy) is None
  True
