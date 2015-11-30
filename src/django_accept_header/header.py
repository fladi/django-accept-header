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

from __future__ import absolute_import

import re

from collections import OrderedDict as kv


class MediaType(object):

    def __init__(self, media_type, q=None, params=None):
        (self._mediatype, self._subtype) = media_type.split('/')
        self._quality = q or 1.0
        self._params = params or {}

    def __repr__(self):
        return '<Media Type: {self}>'.format(self=self)

    def __str__(self):
        if len(self.params) > 0:
            p = '; '.join(['{key}={value}'.format(key=k, value=v) for k, v in self.params.items()])
            return '%s; q=%s; %s' % (self.mimetype, self.q, p)
        else:
            return '%s; q=%s' % (self.mimetype, self.q)

    def __getitem__(self, key):
        return self.params.get(key)

    def __eq__(self, other):
        if isinstance(other, MediaType):
            return self.mimetype == other.mimetype
        return self.mimetype == other

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self._compare(other) == -1

    def __gt__(self, other):
        return self._compare(other) > -1

    def matches(self, other_type):
        other = MediaType(other_type)
        if self.all_types:
            return True
        if self.mediatype == other.mediatype and self.all_subtypes:
            return True
        if self.mediatype == other.mediatype and self.subtype == other.subtype:
            return True
        return False

    @property
    def mimetype(self):
        return '{mediatype}/{subtype}'.format(
            mediatype=self._mediatype,
            subtype=self._subtype
        )

    @property
    def mediatype(self):
        return self._mediatype

    @property
    def subtype(self):
        return self._subtype

    @property
    def quality(self):
        return self._quality

    @property
    def q(self):
        return self.quality

    @property
    def params(self):
        return self._params

    @property
    def all_types(self):
        return self.mediatype == '*' and self.subtype == '*'

    @property
    def all_subtypes(self):
        return self.subtype == '*'

    def _compare(self, other):
        if self.quality > other.quality:
            return -1
        elif self.quality < other.quality:
            return 1
        elif (not self.all_subtypes and other.all_subtypes) or\
                (not self.all_types and other.all_types):
            return -1
        elif (self.all_subtypes and not other.all_subtypes) or\
                (self.all_types and not other.all_types):
            return 1
        elif len(self.params) > len(other.params):
            return -1
        elif len(self.params) == len(other.params):
            return 0
        else:
            return 1


def parse(value):
    results = []
    if not value:
        return results
    value = re.sub(r'^Accept\:\s', '', value)
    for media_range in [m.strip() for m in value.split(',') if m]:
        parts = media_range.split(";")
        media_type = parts.pop(0).strip()
        params = []
        q = 1.0
        for part in parts:
            (key, value) = part.lstrip().split("=", 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            if key == "q":
                try:
                    q = float(value)
                except ValueError:
                    pass
            else:
                params.append((key, value))
        results.append(
            MediaType(media_type, q, kv(params))
        )
    results.sort()
    return results
