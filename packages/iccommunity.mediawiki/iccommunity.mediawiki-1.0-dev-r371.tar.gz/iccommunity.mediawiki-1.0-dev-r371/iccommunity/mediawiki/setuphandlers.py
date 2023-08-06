# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setuphandlers.py 297 2008-06-18 20:11:11Z crocha $
#
# end: Platecom header
""" iccommunity.mediawiki setup handlers.
"""
from StringIO import StringIO

from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.component import getUtility
from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite, IPossibleSite
from Products.CMFCore.utils import getToolByName
from Products.Five.site.localsite import enableLocalSiteHook

import interfaces
from preferences import icCommunityManagementMediawikiRolesMapper, \
    icCommunityManagementMediawikiSQLServer
from config import HAS_PLONE3
from config import DEPENDENCIES

import transaction

def setup_site(context):
    """Site setup"""
    sm = context.getSiteManager()

    if not sm.queryUtility(interfaces.IicCommunityManagementMediawikiRolesMapper,
                           name='iccommunity.configuration'):
        if HAS_PLONE3:
            sm.registerUtility(icCommunityManagementMediawikiRolesMapper(),
                               interfaces.IicCommunityManagementMediawikiRolesMapper,
                               'iccommunity.configuration')
        else:
            sm.registerUtility(interfaces.IicCommunityManagementMediawikiRolesMapper,
                               icCommunityManagementMediawikiRolesMapper(),
                               'iccommunity.configuration')

    if not sm.queryUtility(interfaces.IicCommunityManagementMediawikiSQLServer,
                           name='iccommunity.configuration'):
        if HAS_PLONE3:
            sm.registerUtility(icCommunityManagementMediawikiSQLServer(),
                               interfaces.IicCommunityManagementMediawikiSQLServer,
                               'iccommunity.configuration')
        else:
            sm.registerUtility(interfaces.IicCommunityManagementMediawikiSQLServer,
                               icCommunityManagementMediawikiSQLServer(),
                               'iccommunity.configuration')

def setup_various(context):
  """Import various settings.

  This provisional handler will be removed again as soon as full handlers
  are implemented for these steps.
  """
  site = context.getSite()
  setup_site(site)

