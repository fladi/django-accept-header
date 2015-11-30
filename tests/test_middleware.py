# -*- coding: utf-8 -*-
# Copyright (c) 2015, Rhys Elsmore <me@rhys.io>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""django-accept-header middleware test suite."""

from __future__ import absolute_import

import types
import unittest

from mock import Mock

from django_accept_header.middleware import AcceptMiddleware
from django_accept_header.header import MediaType


class AcceptMiddlewareTest(unittest.TestCase):

    def setUp(self):
        self.am = AcceptMiddleware()

    def test_process_request_returns_none(self):
        request = Mock(META={})
        self.assertIsNone(self.am.process_request(request), None)

    def test_process_request_sets_accepts(self):
        request = Mock(META={})
        self.am.process_request(request)
        self.assertIsInstance(request.accepts, types.FunctionType)

    def test_process_request_sets_accepted_types(self):
        request = Mock(
            META={
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        self.am.process_request(request)
        self.assertIsInstance(request.accepted_types, list)

    def test_process_request_correct_accepted_types(self):
        request = Mock(
            META={
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        expected_types = [
            MediaType('text/html'),
            MediaType('application/xhtml+xml'),
            MediaType('application/xml', 0.9),
            MediaType('*/*', 0.8)
        ]
        self.am.process_request(request)
        self.assertListEqual(
            request.accepted_types,
            expected_types
        )

    def test_process_request_accepts(self):
        request = Mock(
            META={
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9'
            }
        )
        self.am.process_request(request)
        self.assertTrue(request.accepts('text/html'))
        self.assertTrue(request.accepts('application/xhtml+xml'))
        self.assertTrue(request.accepts('application/xml'))
        self.assertFalse(request.accepts('image/png'))
