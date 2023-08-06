import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from collective.portlet.contentsearch.tests import base

class TestSetup(base.FunctionalTestCase):

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

def test_suite():
    return unittest.TestSuite([
        # Demonstrate the main content types
#        ztc.FunctionalDocFileSuite(
#            'README.txt', package='mall.mallcontent',
#            test_class=TestSetup,
#            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

#        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'tests/integration.txt', package='collective.portlet.contentsearch',
            test_class=base.TestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Unit tests
#        doctestunit.DocFileSuite(
#            'tests/unittest.txt', package='mall.mallcontent',
#            setUp=testing.setUp, tearDown=testing.tearDown,
#            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
