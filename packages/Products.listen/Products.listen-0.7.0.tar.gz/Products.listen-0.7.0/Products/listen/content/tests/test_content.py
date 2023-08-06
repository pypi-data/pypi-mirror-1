##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test listen content.

"""

import unittest

# Get our monkeys lined up

from zope.app.component.hooks import setSite, setHooks
from zope.component.testing import tearDown as zcTearDown
from zope.testing import doctest

from Products.listen.interfaces import IMemberLookup
from Products.listen.interfaces import IListLookup
from Products.listen.tests.layer import ListenLayer
from Products.listen.tests.layer import LastLayer
from Products.listen.utilities.list_lookup import ListLookup
from Products.listen.utilities.token_to_email import MemberToEmail
from Products.listen.content.tests import start_log_capture, stop_log_capture

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE # | doctest.REPORT_NDIFF

def test_suite():
    import unittest
    from Testing.ZopeTestCase import FunctionalDocTestSuite
    from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
    listen_layer_suites = (
            FunctionalDocTestSuite('Products.listen.content.digest',
                                   setUp=setup_utility,
                                   tearDown=teardown_logging,
                                   test_class=FunctionalTestCase,
                                   optionflags=optionflags),
            )

    # XXX for some reason these tests will fail unless the entire ZCA
    # is torn down after each test.  putting them in their own layer
    # which is put at the end of the layer hierarchy so they will be
    # run last, since tearing down the ZCA will break other tests
    last_layer_suites = (
            FunctionalDocTestSuite('Products.listen.content.mailinglist',
                                   setUp=setup_listen_components,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase),
            FunctionalDocTestSuite('Products.listen.content.subscriptions',
                                   setUp=setup_utility,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase,
                                   optionflags=optionflags),
            FunctionalDocTestSuite('Products.listen.content.membership_handlers',
                                   setUp=setup_utility,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase),
            FunctionalDocTestSuite('Products.listen.content.membership_policies',
                                   setUp=setup_utility,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase),
            FunctionalDocTestSuite('Products.listen.content.send_mail',
                                   setUp=setup_utility,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase),
            FunctionalDocTestSuite('Products.listen.content.post_policies',
                                   setUp=setup_utility,
                                   tearDown=tearDown,
                                   test_class=FunctionalTestCase)
            )
    for suite in listen_layer_suites:
        suite.layer = ListenLayer

    for suite in last_layer_suites:
        suite.layer = LastLayer

    all_tests = unittest.TestSuite(listen_layer_suites +
                                   last_layer_suites +
            (FunctionalDocTestSuite('Products.listen.content.mailboxer_list',
                                   setUp=setup_logging,
                                   tearDown=teardown_logging),
            ))
    return all_tests

def setup_listen_components(self):
    """ register all the components for the listen product """
    setup_utility(self)
    from Products.Five import zcml
    import Products.listen
    import Products.GenericSetup
    zcml.load_config('meta.zcml', Products.GenericSetup)
    zcml.load_config('configure.zcml', Products.GenericSetup)
    zcml.load_config('meta.zcml', Products.CMFPlone)
    zcml.load_config('configure.zcml', Products.listen)

def setup_utility(self):
     """ register the IMemberLookup utility with the portal """
     portal = self.portal
     import Products.Five
     from Products.Five import zcml
     zcml.load_config('meta.zcml', Products.Five)
     zcml.load_config('permissions.zcml', Products.Five)
     zcml.load_config("configure.zcml", Products.Five.site)
     from Products.listen.utilities import tests
     zcml.load_config('configure.zcml', tests)
     from Products.listen.content import tests as content_tests
     zcml.load_config('configure.zcml', content_tests)

     site = portal
     setSite(site)
     sm = site.getSiteManager()
     member_to_email_utility = MemberToEmail()
     sm.registerUtility(member_to_email_utility, IMemberLookup)
     sm.registerUtility(ListLookup('list_lookup'), IListLookup)
     setHooks()
     setup_logging()

def setup_logging(*args, **kw):
    start_log_capture('listen')

def teardown_logging(*args, **kw):
    stop_log_capture('listen')    

def tearDown(*args, **kw):
    stop_log_capture('listen')
    zcTearDown(*args, **kw)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
