import unittest

from Testing import ZopeTestCase as ztc

from plonehrm.checklist.tests.base import BaseTestCase


def test_suite():
    return unittest.TestSuite([
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
                'doc/overview.txt', package='plonehrm.checklist',
                test_class=BaseTestCase),
        ztc.ZopeDocFileSuite(
                'doc/checklist-technical.txt', package='plonehrm.checklist',
                test_class=BaseTestCase),
        ])
