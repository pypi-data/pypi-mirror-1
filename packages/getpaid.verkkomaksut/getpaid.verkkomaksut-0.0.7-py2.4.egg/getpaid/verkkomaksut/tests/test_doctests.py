import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import getpaid.verkkomaksut
import Products.PloneGetPaid

class TestCase(ptc.FunctionalTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(getpaid.verkkomaksut)
#            zcml.load_config('configure.zcml', getpaid.verkkomaksut)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)


def test_suite():
    return unittest.TestSuite([

        # Unit tests for adapters
        doctestunit.DocFileSuite(
            'tests/unittests/adapters_unittests.txt', package='getpaid.verkkomaksut',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Unit tests for utilities
        doctestunit.DocFileSuite(
            'tests/unittests/utilities_unittests.txt', package='getpaid.verkkomaksut',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        #doctestunit.DocTestSuite(
        #    module='getpaid.verkkomaksut.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='getpaid.verkkomaksut',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='getpaid.verkkomaksut',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'README.txt', package='getpaid.verkkomaksut',
            test_class=TestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
