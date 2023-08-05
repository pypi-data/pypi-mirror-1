import unittest
#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc
from base import BaseTestCase


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.editskinswitcher',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.editskinswitcher.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package='collective.editskinswitcher',
            test_class=BaseTestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.editskinswitcher',
        #    test_class=BaseTestCase),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
