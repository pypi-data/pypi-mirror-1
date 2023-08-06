"""
Mail related doctests
"""

import unittest
from zope.testing import doctest

from Testing.ZopeTestCase import FunctionalDocFileSuite
#from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.tests.utils import MockMailHost

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)
from collective.langMailHost.tests.base import MailHostFunctionalTestCase

#class MockMailHostTestCase(PloneTestCase.FunctionalTestCase):
class MockMailHostTestCase(MailHostFunctionalTestCase):

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost('MailHost')

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost


def test_suite():
    return unittest.TestSuite((
        FunctionalDocFileSuite('tests/mails.txt',
                               optionflags=OPTIONFLAGS,
                               package='collective.langMailHost',
                               test_class=MockMailHostTestCase),
        ))
