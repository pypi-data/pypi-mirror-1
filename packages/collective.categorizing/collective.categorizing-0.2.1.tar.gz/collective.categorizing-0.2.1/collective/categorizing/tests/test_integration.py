import unittest
import doctest
from Testing import ZopeTestCase as ztc
from collective.categorizing.tests import base

class CollectiveCategorizingIntegrationTestCase(base.CollectiveCategorizingTestCase):
    """Base class used for test cases
    """

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """
        self.setRoles(('Manager',))

def test_suite():
    return unittest.TestSuite([

        # Integration tests for adapters.
        ztc.ZopeDocFileSuite(
            'tests/integration/adapter_integration.txt', package='collective.categorizing',
            test_class=CollectiveCategorizingIntegrationTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Integration tests for contents.
        ztc.ZopeDocFileSuite(
            'tests/integration/content_integration.txt', package='collective.categorizing',
            test_class=CollectiveCategorizingIntegrationTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Integration tests for utilities.
        ztc.ZopeDocFileSuite(
            'tests/integration/utility_integration.txt', package='collective.categorizing',
            test_class=CollectiveCategorizingIntegrationTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Integration tests for utilities.
        ztc.ZopeDocFileSuite(
            'tests/integration/view_integration.txt', package='collective.categorizing',
            test_class=CollectiveCategorizingIntegrationTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
