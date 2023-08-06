# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_utilities.py 297 2008-06-18 20:11:11Z crocha $
#
# end: Platecom header
"""Test the catalog indexes added by OntoCatalog.
"""

import unittest
from zope.component import getUtility

from iccommunity.mediawiki.tests.base import MediawikiTestCase
from iccommunity.mediawiki.interfaces import IicCommunityManagementMediawikiRolesMapper


class TestMediawikiUtilities(MediawikiTestCase):
    """Testing utilities"""

    def test_get_parsed_rolemap(self):
        """Testing the get_parsed_rolemap method"""
        self.loginAsPortalOwner()
        settings = getUtility(IicCommunityManagementMediawikiRolesMapper,
                              name='iccommunity.configuration',
                              context=self.portal)
        settings.rolemap = [u'Role;Role', u'Another role;    A mediawiki role ']
        expected = [(u'Role', u'Role'), (u'Another role', u'A mediawiki role')]
        self.assertEquals(settings.get_parsed_rolemap(), expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMediawikiUtilities))
    return suite
