import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from currency.converter.tests import base

class TestSetup(base.CurrencyConverterFunctionalTestCase):

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

def test_suite():
    return unittest.TestSuite([
        # Demonstrate the main content types
#        ztc.ZopeDocFileSuite(
        ztc.FunctionalDocFileSuite(
            'tests/functional.txt', package='currency.converter',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

#        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'tests/integration.txt', package='currency.converter',
            test_class=base.CurrencyConverterTestCase,
#            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Unit tests
        doctestunit.DocFileSuite(
            'tests/unittest.txt', package='currency.converter',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
