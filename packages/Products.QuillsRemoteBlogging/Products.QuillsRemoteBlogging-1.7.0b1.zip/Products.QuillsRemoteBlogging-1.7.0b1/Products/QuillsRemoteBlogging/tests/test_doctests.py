# Standard library imports
import unittest
from doctest import DocTestSuite

# Zope imports
import zope.component.testing


def setUp(test):
    pass

suites = (
    DocTestSuite('Products.QuillsRemoteBlogging.uidmanager',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    DocTestSuite('Products.QuillsRemoteBlogging.usermanager',
                 setUp=zope.component.testing.setUp,
                 tearDown=zope.component.testing.tearDown),
    )

def test_suite():
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')