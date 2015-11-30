#!/usr/bin/env python
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

"""django-accept-header parser test suite."""

import unittest

from django_accept_header.header import parse, MediaType


class ParserTestCase(unittest.TestCase):
    """Parser test cases."""

    def test_empty_value(self):
        self.assertEquals(parse(''), [])

    def test_none_value(self):
        self.assertEquals(parse(None), [])

    def test_parse_simple_header(self):
        m = [MediaType('application/json')]
        self.assertEquals(m, parse('application/json'))

    def test_accept_header_still_included(self):
        m = [MediaType('application/json')]
        self.assertEquals(m, parse('Accept: application/json'))

    def test_prefer_most_specific_type(self):
        m = [
            MediaType('application/json'),
            MediaType('application/*', 0.2),
        ]
        self.assertEquals(
            parse('application/*; q=0.2, application/json'),
            m
        )

    def test_media_type_parameter_with_quotes(self):
        self.assertEquals(
            parse('application/*; q="0.2"'),
            [MediaType('application/*', 0.2)]
        )
        self.assertEquals(
            parse("application/*; q='0.2'"),
            [MediaType('application/*', 0.2)]
        )
        self.assertEquals(
            parse('application/*; q=0.2; test="moop"'),
            [MediaType('application/*', 0.2, {"test": "moop"})]
        )
        self.assertEquals(
            parse("application/*; q=0.2; test='moop'"),
            [MediaType('application/*', 0.2, {"test": "moop"})]
        )

    def test_special_characters(self):
        self.assertEquals(
            parse('application/*; test=_0-2'),
            [MediaType('application/*', params={"test": "_0-2"})]
        )
        self.assertEquals(
            parse("application/*; test=_0-2'"),
            [MediaType('application/*', params={"test": "_0-2"})]
        )

    def test_non_valid_q_value(self):
        self.assertEquals(
            parse('application/*; q=_0-2'),
            [MediaType('application/*', 1.0)]
        )

    def test_elaborate_accept_header(self):
        self.assertEquals(
            parse('text/*, text/html, text/html;level=1, */*'),
            [
                MediaType('text/html', params={'level': '1'}),
                MediaType('text/html'),
                MediaType('text/*'),
                MediaType('*/*')
            ]
        )

    def test_real_world_header(self):
        m = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.assertEquals(
            parse(m),
            [
                MediaType('text/html'),
                MediaType('application/xhtml+xml'),
                MediaType('application/xml', q=0.9),
                MediaType('*/*', q=0.8)
            ]
        )

    def test_parse_broken_accept_header(self):
        header = ('text/xml,application/xml,application/xhtml+xml,') +\
                 ('text/html;q=0.9,text/plain;q=0.8,image/*,,*/*;q=0.5')
        self.assertEquals(
            parse(header),
            [
                MediaType('text/xml'),
                MediaType('application/xml'),
                MediaType('application/xhtml+xml'),
                MediaType('image/*'),
                MediaType('text/html', q=0.9),
                MediaType('text/plain', q=0.8),
                MediaType('*/*', q=0.5)
            ]
        )


class MediaTypeTestCase(unittest.TestCase):
    """Media Type test cases."""

    def test_equal_media_types(self):
        self.assertEquals(
            MediaType('application/json'),
            MediaType('application/json')
        )
        self.assertEquals(
            MediaType('application/json', params={'test': '2'}),
            MediaType('application/json', params={'test': '2'})
        )
        self.assertEquals(
            MediaType('application/json'),
            'application/json'
        )

    def test_unequal_media_types(self):
        self.assertNotEquals(
            MediaType('application/json'),
            MediaType('text/plain')
        )
        self.assertNotEquals(
            MediaType('application/json', params={'test': '2'}),
            MediaType('text/plain', params={'test': '2'})
        )
        self.assertNotEquals(
            MediaType('application/json'),
            'text/plain'
        )

    def test_more_specific(self):
        self.assertLess(
            MediaType('application/*'),
            MediaType('text/plain', q=0.8)
        )
        self.assertLess(
            MediaType('application/json', params={'test': '2'}),
            MediaType('application/*')
        )
        self.assertLess(
            MediaType('application/json', q=0.5, params={'test': '2'}),
            MediaType('application/json', q=0.5)
        )
        self.assertLess(
            MediaType('application/json'),
            MediaType('application/*')
        )
        self.assertLess(
            MediaType('application/*'),
            MediaType('*/*')
        )

    def test_less_specific(self):
        self.assertGreater(
            MediaType('text/plain', q=0.8),
            MediaType('application/*')
        )
        self.assertGreater(
            MediaType('application/*'),
            MediaType('application/json', params={'test': '2'})
        )
        self.assertGreater(
            MediaType('application/json', q=0.5),
            MediaType('application/json', q=0.5, params={'test': '2'})
        )
        self.assertGreater(
            MediaType('application/*'),
            MediaType('application/json')
        )
        self.assertGreater(
            MediaType('*/*'),
            MediaType('application/*')
        )

    def test_matches_mediatypes(self):
        ma = MediaType('*/*')
        self.assertTrue(ma.matches('application/*'))
        self.assertTrue(ma.matches('application/json'))
        self.assertTrue(ma.matches('text/plain'))

    def test_matches_mediatypes_specific(self):
        ma = MediaType('text/*')
        self.assertFalse(ma.matches('application/*'))
        self.assertFalse(ma.matches('application/json'))
        self.assertTrue(ma.matches('text/*'))
        self.assertTrue(ma.matches('text/plain'))

    def test_matches_subtypes(self):
        ma = MediaType('image/png')
        self.assertFalse(ma.matches('application/json'))
        self.assertFalse(ma.matches('image/*'))
        self.assertFalse(ma.matches('image/jpeg'))
        self.assertTrue(ma.matches('image/png'))

    def test_media_types(self):
        self.assertEquals(
            MediaType('application/json').mediatype,
            'application'
        )
        self.assertEquals(
            MediaType('application/*').mediatype,
            'application'
        )
        self.assertEquals(
            MediaType('*/*').mediatype,
            '*'
        )

    def test_subtypes(self):
        self.assertEquals(
            MediaType('application/json').subtype,
            'json'
        )
        self.assertEquals(
            MediaType('application/*').subtype,
            '*'
        )

    def test_all_subtypes(self):
        self.assertFalse(MediaType('application/json').all_subtypes)
        self.assertTrue(MediaType('application/*').all_subtypes)
        self.assertTrue(MediaType('*/*').all_subtypes)

    def test_all_types(self):
        self.assertFalse(MediaType('application/json').all_types)
        self.assertFalse(MediaType('application/*').all_types)
        self.assertTrue(MediaType('*/*').all_types)

    def test_representation(self):
        header = 'application/json; q=0.2; level=1; test=2; something=3'
        m = parse(header)[0]
        self.assertEquals(
            repr(m),
            '<Media Type: {}>'.format(header)
        )

    def test_string_representation(self):
        header = 'application/json; q=0.2'
        m = parse(header)[0]
        self.assertEquals(
            str(m),
            header
        )

    def test_string_representation_parameter(self):
        header = 'application/json; q=0.2; level=1; test=2; something=3'
        m = parse(header)[0]
        self.assertEquals(
            str(m),
            header
        )

    def test_getitem_param_exists(self):
        m = MediaType('application/json', params={'test': '2'})
        self.assertEqual(m['test'], '2')

    def test_getitem_param_none(self):
        m = MediaType('application/json')
        self.assertIsNone(m['test'])
