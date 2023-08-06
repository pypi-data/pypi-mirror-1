# -*- coding: utf-8 -*-

from zope.schema import Field
from zope.schema.interfaces import WrongType
from zope.interface import implements
from zope.interface.verify import verifyClass
from zope.interface.interfaces import IInterface
from dolmen.field import IClassField


class GlobalClass(Field):
    """
    A GlobalClass field stores a Class type value.
    The class stored is represented by an interface.

      >>> from zope.schema import TextLine
      >>> from zope.interface import Interface

      >>> class IDummy(Interface):
      ...     def shall_fail():
      ...         pass

      >>> class Dummy(object):
      ...     pass

   Of course, it must be a valid interface.

      >>> field = GlobalClass(
      ...             title=u'a class field',
      ...             interface=object
      ...             )
      Traceback (most recent call last):
      ...
      WrongType: <type 'object'> is not a valid Interface

   The interface will be used to validate the class.
   
      >>> field = GlobalClass(
      ...             title=u'a class field',
      ...             interface=IDummy
      ...             )

      >>> field.interface
      <InterfaceClass dolmen.field.fields.IDummy>
      >>> IClassField.providedBy(field)
      True

    In a first time, we make sure the class implements the needed interface:

      >>> field._validate(Dummy)
      Traceback (most recent call last):
      ...
      WrongType: <class 'dolmen.field.fields.Dummy'> does not implement <InterfaceClass dolmen.field.fields.IDummy>
      
      >>> from zope.interface import classImplements
      >>> classImplements(Dummy, IDummy)
      >>> IDummy.implementedBy(Dummy)
      True

    Then the interface acts as a strict validator:

      >>> field._validate(Dummy)
      Traceback (most recent call last):
      ...
      BrokenImplementation: An object has failed to implement interface <InterfaceClass dolmen.field.fields.IDummy>
      <BLANKLINE>
              The shall_fail attribute was not provided.
      <BLANKLINE>

      >>> Dummy.shall_fail = lambda x: u'not'
      >>> field._validate(Dummy) is None
      True
    """
    implements(IClassField)

    def __init__(self, interface, **kw):
        if not IInterface.providedBy(interface):
            raise WrongType, u"%r is not a valid Interface" % interface

        self.interface = interface
        super(GlobalClass, self).__init__(**kw)


    def _validate(self, value):
        super(GlobalClass, self)._validate(value)

        # schema has to be provided by value
        if not self.interface.implementedBy(value):
            raise WrongType, u"%r does not implement %r" % (value,
                                                            self.interface)

        # check the value against schema
        verifyClass(self.interface, value)
