import unittest
import doctest

#from zope.testing import doctestunit
#from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from collective.categorizing.tests import base

#import StringIO
#from Products.CMFCore.utils import getToolByName

class TestSetup(base.CollectiveCategorizingFunctionalTestCase):

    def afterSetUp( self ):
        """After SetUp"""

        self.setRoles(('Manager',))

def test_suite():
    return unittest.TestSuite([

        ## Content Type related tests.
        ztc.FunctionalDocFileSuite(
            'tests/functional/content_functional.txt', package='collective.categorizing',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
