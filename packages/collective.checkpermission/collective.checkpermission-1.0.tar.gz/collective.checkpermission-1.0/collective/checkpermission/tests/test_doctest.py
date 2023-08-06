import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.checkpermission

from collective.checkpermission.tests import base

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.checkpermission)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'check.txt', package='collective.checkpermission',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='collective.checkpermission.check',
            setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.checkpermission',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'check.txt', package='collective.checkpermission',
             test_class=base.FunctionalTestCase),
        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.checkpermission',
        #    test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
