# -*- coding: utf-8 -*-
import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from collective.collection.alphabetic.tests import base

class TestSetup(base.CollectionAlphabeticFunctionalTestCase):

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocFileSuite(
            'tests/unittest.txt', package='collective.collection.alphabetic',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.FunctionalDocFileSuite(
            'tests/functional.txt', package='collective.collection.alphabetic',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
