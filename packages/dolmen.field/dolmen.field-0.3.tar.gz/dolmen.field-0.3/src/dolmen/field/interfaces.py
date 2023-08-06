# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import InterfaceField
from zope.schema.interfaces import IField


class IClassField(IField):
    """Field requiring a valid class with an interface to validate.
    """
    schema = InterfaceField(
        required = False,
        title = u"Validation interface",
        description = u"Mandatory interface, needed to validate the value.",
        default = Interface
        )
