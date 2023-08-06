import unittest
#import doctest
#from zope.testing import doctestunit
#from zope.component import testing, eventtesting
#from Testing import ZopeTestCase as ztc
from collective.categorizing.tests import base

class TestSetup(base.CollectiveCategorizingTestCase):

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

def test_suite():
    return unittest.TestSuite([

        # Unit tests
#        doctestunit.DocFileSuite(
#            'tests/unittest/utility.txt', package='collective.categorizing',
#            setUp=testing.setUp, tearDown=testing.tearDown,
#            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
