"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.
Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""
# Zope imports
from Testing import ZopeTestCase

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
# More Plone imports
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.remoteblogging.interfaces import IUIDManager

# Local imports


# Let Zope know about QuillsRemoteBlogging
ZopeTestCase.installProduct('Quills')
ZopeTestCase.installProduct('QuillsRemoteBlogging')
ZopeTestCase.installProduct('MetaWeblogPASPlugin')

# Set up a Plone site, and apply the ATTrackback extension profile
setupPloneSite(products=['Quills',
                         'MetaWeblogPASPlugin',
                         'QuillsRemoteBlogging',
                         ])


class QuillsRemoteBloggingDocTestCase(PloneTestCase):
    """Base class for integration tests for the 'QuillsRemoteBlogging' product.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Weblog', id='weblog')
        self.mwenabled = self.portal.weblog
        self.appkey = IUIDManager(self.mwenabled).getUID()
        self.blogid = self.appkey
        mtool = getToolByName(self.portal, 'portal_membership')
        self.bloguserid = mtool.getAuthenticatedMember().getId()
