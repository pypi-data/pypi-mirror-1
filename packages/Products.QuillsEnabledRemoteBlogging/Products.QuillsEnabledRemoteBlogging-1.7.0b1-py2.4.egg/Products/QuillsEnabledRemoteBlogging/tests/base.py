"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.
Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""
# Zope imports
from Testing import ZopeTestCase
from zope.interface import alsoProvides

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
# More Plone imports
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEnhanced
from quills.remoteblogging.interfaces import IUIDManager

# Local imports


# Let Zope know about QuillsRemoteBlogging
ZopeTestCase.installProduct('QuillsEnabled')
ZopeTestCase.installProduct('QuillsEnabledRemoteBlogging')
ZopeTestCase.installProduct('MetaWeblogPASPlugin')

# Set up a Plone site, and apply the ATTrackback extension profile
setupPloneSite(products=['QuillsEnabled',
                         'MetaWeblogPASPlugin',
                         'QuillsEnabledRemoteBlogging',
                         ])


class QuillsEnabledRemoteBloggingDocTestCase(PloneTestCase):
    """Base class for integration tests for the 'QuillsRemoteBlogging' product.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', id='weblog')
        folder = self.portal.weblog
        #self.portal.portal_workflow.doActionFor(folder, 'publish')
        alsoProvides(folder, IWeblogEnhanced)
        self.weblog = IWeblog(folder)
        self.mwenabled = self.portal.weblog
        self.appkey = IUIDManager(self.mwenabled).getUID()
        self.blogid = self.appkey
        mtool = getToolByName(self.portal, 'portal_membership')
        self.bloguserid = mtool.getAuthenticatedMember().getId()
