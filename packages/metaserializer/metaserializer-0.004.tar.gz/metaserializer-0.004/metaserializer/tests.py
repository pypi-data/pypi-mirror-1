#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <23-Feb-2010 17:45:46 PST by rich@noir.com>

"""
Test cases for metaserializer.
"""

__docformat__ = 'epytext'

from StringIO import StringIO

import unittest
import nose

from metaserializer import MetaSerializer
from metaserializer.mspickle import PickleDefault, PickleHighest
from metaserializer.msyaml import YAML
#from metaserializer.msjson import JSON

class Base(unittest.TestCase):
    def setUp(self):
        self.serializer = MetaSerializer()
        self.assertTrue(isinstance(self.serializer.name, str))
        self.stringfile = StringIO()

    def tearDown(self):
        pass


class TestBasics(Base):
    def test_dump(self):
        self.assertRaises(NotImplementedError, self.serializer.dump, 'test', self.stringfile)

    def test_load(self):
        self.assertRaises(NotImplementedError, self.serializer.load, self.stringfile)

    def test_dumps(self):
        self.assertRaises(NotImplementedError, self.serializer.dumps, 'test')

    def test_loads(self):
        self.assertRaises(NotImplementedError, self.serializer.loads, 'test')

def test_generator():
    samples = [None, True, False, '', (), [], {}, 'test1, 2', (1, 2, 3), [4, 5, 6], {7: 8, 9: 10, 11: 12}]

    #string_only = [JSON()]
    string_only = []
    file_only = []
    both = [PickleDefault(), PickleHighest(), YAML()]

    for serializer in string_only + both:
        for exp in [samples] + samples:
            yield (stringLoopback, serializer, exp)

    for serializer in file_only + both:
        for exp in [samples] + samples:
            yield (fileLoopback, serializer, exp)

def stringLoopback(serializer, obj):
    s = serializer.dumps(obj)
    nose.tools.assert_true(isinstance(s, str))
    o = serializer.loads(s)
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
