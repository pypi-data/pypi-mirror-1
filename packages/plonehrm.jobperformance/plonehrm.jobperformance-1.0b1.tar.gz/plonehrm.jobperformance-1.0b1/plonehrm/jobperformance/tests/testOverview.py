import unittest
from Testing import ZopeTestCase as ztc
from plonehrm.jobperformance.tests.base import BaseTestCase


def test_suite():
    return unittest.TestSuite([
        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'overview.txt', package='plonehrm.jobperformance.doc',
            test_class=BaseTestCase),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
