# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: install.py 235 2008-06-10 20:21:40Z crocha $
#
# end: Platecom header
"""Install the product
"""
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr

from iccommunity.mediawiki import GLOBALS
from iccommunity.mediawiki.config import DEPENDENCIES

import transaction

def install_dependencies(context):
    """Install dependencies"""
    quickinstaller = getToolByName(context, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if quickinstaller.isProductInstalled(product):
            quickinstaller.reinstallProducts([product])
            transaction.savepoint()
        else:
            quickinstaller.installProduct(product)
            transaction.savepoint()


def install(self):
    """External module to install the product.

    @type self: PloneSite
    @param self: The Plone site object

    @rtype: StringIO
    @return: Messages from the install process
    """
    out = StringIO()

    install_dependencies(self)
    # Run all import steps for iccommunity.mediawiki
    setup_tool = getToolByName(self, 'portal_setup')
    if shasattr(setup_tool, 'runAllImportStepsFromProfile'):
        # Plone 3
        setup_tool.runAllImportStepsFromProfile('profile-iccommunity.mediawiki:default')
    else:
        # Plone 2.5.
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-iccommunity.mediawiki:default')
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext(old_context)

    return out.getvalue()


def uninstall( self ):
    """Uninstall method.
    """
    out = StringIO()
    print >> out, "Uninstalling"
    return out.getvalue()

