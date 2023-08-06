# -*- coding: utf-8 -*-

from zope.schema import Field
from zope.schema import interfaces as errors
from zope.interface import implements
from zope.interface.verify import verifyClass
from zope.interface.interfaces import IInterface
from dolmen.field import IClassField


class GlobalClass(Field):
    """A field storing a class implementing a given schema.
    """
    implements(IClassField)

    def __init__(self, schema, **kw):
        if not IInterface.providedBy(schema):
            raise errors.WrongType(u"%r is not a valid Interface" % schema)

        self.schema = schema
        super(GlobalClass, self).__init__(**kw)

    def _validate(self, value):
        super(GlobalClass, self)._validate(value)

        # schema has to be provided by value
        if not self.schema.implementedBy(value):
            raise errors.ConstraintNotSatisfied(
                u"%r does not implement %r" % (value, self.schema))

        # check the value against schema
        verifyClass(self.schema, value)
