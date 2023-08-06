# Standard library imports
from StringIO import StringIO

# Zope imports
import transaction

# CMF imports
from Products.CMFCore.utils import getToolByName

# MetaWeblogPASPlugin import
from Products.MetaWeblogPASPlugin import config


def install(self):
    """Install QuillsRemoteBlogging
    """
    out = StringIO()
    portal = getToolByName(self,'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    print >> out, u"Installing dependency %s:" % config.PROJECTNAME
    quickinstaller.installProduct(config.PROJECTNAME)
    transaction.savepoint()
    print >> out, u"Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()
