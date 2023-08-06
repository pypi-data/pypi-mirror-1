============
dolmen.field
============

The `dolmen.field` package provides additional generalist fields for
Zope's Formlib. It aims to complete the original formlib set with
simple yet useful fields.


Configuration fields
--------------------

The configuration fields are used for description and constraints, to
impose a consistent schema and data model.

  - `ClassField` : A field requiring a valid class with an interface
    to validate. Mainly used for factories and other components that
    need to store interface with a possibility to check and verify the
    consistency of the given value.


About
-----

This package is part of the Dolmen project. See
`http://tracker.trollfot.org/wiki/Dolmen` for more information.
