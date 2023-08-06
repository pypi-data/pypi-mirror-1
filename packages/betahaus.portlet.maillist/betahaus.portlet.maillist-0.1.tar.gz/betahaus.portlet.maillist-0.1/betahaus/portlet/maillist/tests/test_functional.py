"""
Mail related doctests
"""

import unittest
from zope.testing import doctest

from Testing.ZopeTestCase import FunctionalDocFileSuite
from betahaus.portlet.maillist.tests.base import FunctionalTestCase

from Products.CMFPlone.tests.utils import MockMailHost

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class MyMockMailHost(MockMailHost):
    """Need to extend the MockMailHost to save all fields of the message
    """
    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        """
        Basically construct an email.Message from the given params to make sure
        everything is ok and store the results in the messages instance var.
        """
        self.messages.append({'message': message,
                              'mto': mto,
                              'mfrom': mfrom,
                              'subject': subject,
                              'encode': encode,
                              })
        
class MockMailHostTestCase(FunctionalTestCase):

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MyMockMailHost('MailHost')

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost


def test_suite():
    return unittest.TestSuite((
        FunctionalDocFileSuite('tests/functional.txt',
                               optionflags=OPTIONFLAGS,
                               package='betahaus.portlet.maillist',
                               test_class=MockMailHostTestCase),
        ))
