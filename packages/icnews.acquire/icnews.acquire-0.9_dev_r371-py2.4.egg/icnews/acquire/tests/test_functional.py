"""Functional tests
"""

import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from icnews.acquire.config import *
import base

def test_suite():
    return unittest.TestSuite([
        # Test the SQL server configlet
        ztc.ZopeDocFileSuite(
            'tests/sql_server_configlet.txt', package=PACKAGENAME,
            test_class=base.ICNewsAcquireFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the generated RSS
        ztc.ZopeDocFileSuite(
            'tests/rss.txt', package=PACKAGENAME,
            test_class=base.ICNewsAcquireFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')