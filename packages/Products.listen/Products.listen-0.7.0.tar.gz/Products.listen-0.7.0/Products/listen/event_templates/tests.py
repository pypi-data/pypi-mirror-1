from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.listen.tests.layer import ListenLayer
from Products.PloneTestCase import PloneTestCase as ptc
from Products.listen.interfaces import IListLookup
from zope.component import getUtility
import unittest

list_id = 'mylist'

class TestManageEvent(ptc.PloneTestCase):

    """test to exercise the manage_event function called from smtp2zope on
       errors"""

    layer = ListenLayer

    def afterSetUp(self):
        """create a mailing list that we can send events to and mock
        the mail host"""
        # XXX this should maybe be done in a layer so it doesn't
        # happen again for each test, but when i put this in the
        # ListenLayer it fails b/c the component registry hasn't yet
        # been set up.
        ml = _createObjectByType('MailingList', self.portal, list_id)
        ml.setTitle('My List')
        ml.mailto = 'mylist@nohost'
        ll = getUtility(IListLookup)
        ll.registerList(ml)
        self.mlist = ml

    def beforeTearDown(self):
        mailhost = self._getMailHost()
        mailhost.messages = []

    def _getMailHost(self):
        # XXX tests fail if we get the mailhost via acquisition, have
        # to use getToolByName :(
        return getToolByName(self.portal, 'MailHost')

    def test_200_error(self):
        headers = {'from': 'johnnywalker@example.com',
                   'to': 'mylist@nohost',
                   }
        status_codes = [200]
        self.mlist.manage_event(status_codes, headers)
        mailhost = self._getMailHost()
        msgs = mailhost.messages
        self.assertEqual(1, len(msgs), 'No error message sent')
        msg = msgs[0]

        self.assertEqual('mylist-manager@nohost', msg['mfrom'])
        self.assertEqual(['johnnywalker@example.com'], msg['mto'])
        self.failUnless('Mailing list error: message too big' in msg['subject'])
        self.failUnless("message that you're trying to send is too big" in msg['msg'])

    def test_default_error(self):
        headers = {'from': 'mister.dewars@example.com',
                   'to': 'mylist@lists.openplans.org',
                   }
        # any unknown status code
        status_codes = [777]
        self.mlist.manage_event(status_codes, headers)
        mailhost = self._getMailHost()
        msgs = mailhost.messages
        self.assertEqual(1, len(msgs), 'No error message sent')
        msg = msgs[0]
        self.assertEqual('mylist-manager@nohost', msg['mfrom'])
        self.assertEqual(['mister.dewars@example.com'], msg['mto'])
        self.failUnless('Mailing list error' in msg['subject'])
        self.failUnless('unknown error' in msg['msg'])

def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestManageEvent),))
