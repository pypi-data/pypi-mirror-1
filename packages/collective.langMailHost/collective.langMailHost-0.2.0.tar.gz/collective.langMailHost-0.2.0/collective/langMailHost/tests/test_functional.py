import unittest
import doctest
from Testing import ZopeTestCase as ztc
from collective.langMailHost.tests import base
from Products.CMFCore.utils import getToolByName

class TestSetup(base.MailHostFunctionalTestCase):

    def afterSetUp( self ):
        """After SetUp"""
        portal = self.portal
        language_tool = getToolByName(portal, 'portal_languages')
        language_tool.addSupportedLanguage('ja')

def test_suite():
    return unittest.TestSuite([

        # Integration tests for adapters.
        ztc.FunctionalDocFileSuite(
            'tests/functional/adapter.txt', package='collective.langMailHost',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
