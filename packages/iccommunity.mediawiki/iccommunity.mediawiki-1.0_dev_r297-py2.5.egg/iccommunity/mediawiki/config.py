# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 278 2008-06-14 02:38:00Z esmenttes $
#
# end: Platecom header
import iccommunity.mediawiki
PROJECTNAME = "iccommunity.mediawiki"
PACKAGE = iccommunity.mediawiki
PACKAGENAME = "iccommunity.mediawiki"
DEPENDENCIES = ['icsemantic.core', 'iccommunity.core']

try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False
