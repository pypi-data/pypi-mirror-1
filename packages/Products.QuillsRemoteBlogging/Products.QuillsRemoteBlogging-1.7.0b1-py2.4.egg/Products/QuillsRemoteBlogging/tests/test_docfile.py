# Standard library imports
import unittest

# Zope imports
from zope.testing import doctest
from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
from Testing import ZopeTestCase

# Plone imports
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite

# Local imports
from Products.QuillsRemoteBlogging import config
from base import QuillsRemoteBloggingDocTestCase


ZOPE_DEPS =  ['Quills', config.PROJECTNAME,]
PLONE_DEPS = ['Quills', config.PROJECTNAME,]

for x in ZOPE_DEPS + PLONE_DEPS:
    ZopeTestCase.installProduct(x)

PloneTestCase.setupPloneSite(products=PLONE_DEPS)

def test_suite():
    suite = unittest.TestSuite(())

    suite.addTest(ZopeDocFileSuite(
        'metaweblogapi.txt',
        package='quills.remoteblogging.tests',
        test_class=QuillsRemoteBloggingDocTestCase,
        optionflags=doctest.ELLIPSIS,
        )
    )

    suite.layer = PloneSite
    return suite
