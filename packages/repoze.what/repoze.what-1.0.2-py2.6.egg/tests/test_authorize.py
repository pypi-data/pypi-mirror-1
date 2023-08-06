# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007, Agendaless Consulting and Contributors.
# Copyright (c) 2008, Florent Aide <florent.aide@gmail.com>.
# Copyright (c) 2008-2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
Tests for the authorization mechanisms.

"""

import unittest

from repoze.what import authorize

from base import FakeLogger
from test_predicates import make_environ


class TestAuthorizationChecker(unittest.TestCase):
    """Tests for the check_authorization() function"""
    
    def test_authorized(self):
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = authorize.has_any_permission('party', 'scream')
        authorize.check_authorization(p, environ)
        info = logger.messages['info']
        assert "Authorization granted" == info[0]
    
    def test_unauthorized(self):
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = authorize.has_any_permission('jump', 'scream',
                                         msg="Go away!")
        try:
            authorize.check_authorization(p, environ)
            self.fail('Authorization must have been rejected')
        except authorize.NotAuthorizedError, e:
            self.assertEqual(str(e), "Go away!")
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: Go away!" == info[0]
    
    def test_unauthorized_with_unicode_message(self):
        # This test is broken on Python 2.4 and 2.5 because the unicode()
        # function doesn't work when converting an exception into an unicode
        # string (this is, to extract its message).
        unicode_msg = u'请登陆'
        logger = FakeLogger()
        environ = make_environ('gustavo', permissions=['watch-tv', 'party',
                                                       'eat'])
        environ['repoze.who.logger'] = logger
        p = authorize.has_any_permission('jump', 'scream',
                                         msg=unicode_msg)
        try:
            authorize.check_authorization(p, environ)
            self.fail('Authorization must have been rejected')
        except authorize.NotAuthorizedError, e:
            self.assertEqual(unicode(e), unicode_msg)
            # Testing the logs:
            info = logger.messages['info']
            assert "Authorization denied: %s" % unicode_msg == info[0]


class TestNotAuthorizedError(unittest.TestCase):
    """Tests for the NotAuthorizedError exception"""
    
    def test_string_representation(self):
        msg = 'You are not the master of Universe'
        exc = authorize.NotAuthorizedError(msg)
        self.assertEqual(msg, str(exc))
