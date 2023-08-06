import unittest
from Testing import ZopeTestCase as ztc
from base import BaseFunctionalTestCase


def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'need_authentication.txt',
            package='collective.editskinswitcher.tests',
            test_class=BaseFunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
