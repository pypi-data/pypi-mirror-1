import unittest
import doctest
import dolmen.field

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite("dolmen.field.fields")
        )
    return suite
