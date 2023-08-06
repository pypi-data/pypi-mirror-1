#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:41:17 PST by rich@noir.com>

"""
Test cases for metaserializer.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

from StringIO import StringIO

import unittest
import nose

from metaserializer import MetaSerializer, SerializerFromMagic
from metaserializer.mspickle import PickleDefault, PickleHighest
from metaserializer.msyaml import YAML
from metaserializer.msjson import JSON
from metaserializer.msphp import PHP
from metaserializer.msplist import plist

class Base(unittest.TestCase):
    def setUp(self):
        self.serializer = MetaSerializer()
        self.assertTrue(isinstance(self.serializer.name, unicode))
        self.stringfile = StringIO()

    def tearDown(self):
        pass


class TestBasics(Base):
    def test_dump(self):
        self.assertRaises(NotImplementedError, self.serializer.dump, 'test', self.stringfile)

    def test_load(self):
        self.assertRaises(NotImplementedError, self.serializer.load, self.stringfile)

    def test_dumpb(self):
        self.assertRaises(NotImplementedError, self.serializer.dumpb, 'test')

    def test_loadb(self):
        self.assertRaises(NotImplementedError, self.serializer.loadb, 'test')

def test_generator():
    samples = [None, True, False, '', (), [], {}, 'test1, 2', (1, 2, 3), [4, 5, 6], {7: 8, 9: 10, 11: 12}]

    #string_only = [JSON()]
    string_only = []
    file_only = []
    broken = [JSON(), PHP(), plist()]
    both_magic = [b'a', b'b', b'c']
    both = [PickleDefault(), PickleHighest(), YAML()]

    for serializer in string_only + both + [SerializerFromMagic(i) for i in both_magic]:
        for exp in [samples] + samples:
            yield (stringLoopback, serializer, exp)

    for serializer in file_only + both:
        for exp in [samples] + samples:
            yield (fileLoopback, serializer, exp)

def stringLoopback(serializer, obj):
    b = serializer.dumpb(obj)
    nose.tools.assert_true(isinstance(b, bytes))
    o = serializer.loadb(b)
    nose.tools.assert_equals(o, obj)

def fileLoopback(serializer, obj):
    stringfile = StringIO()

    serializer.dump(obj, stringfile)
    stringfile.seek(0)
    o = serializer.load(stringfile)
    nose.tools.assert_equals(o, obj)


if __name__ == '__main__':
    nose.main()
    print 'done'
