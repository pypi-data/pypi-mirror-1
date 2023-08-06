# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_functional.py 235 2008-06-10 20:21:40Z crocha $
#
# end: Platecom header
"""Functional tests for OntoCatalog.
"""

import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from iccommunity.mediawiki.config import *
import base

def test_suite():
    return unittest.TestSuite([

        # Test the Wikimedia SQL server configlet 
        ztc.ZopeDocFileSuite(
            'tests/sql_server_configlet.txt', package=PACKAGENAME,
            test_class=base.MediawikiFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the Roles Mapper configlet
        ztc.ZopeDocFileSuite(
            'tests/roles_mapper_configlet.txt', package=PACKAGENAME,
            test_class=base.MediawikiFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')