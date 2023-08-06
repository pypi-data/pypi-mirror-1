#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:38:03 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into two distinct
subclasses both of which are based on the pickle module from the
standard library.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

from metaserializer import MetaSerializer, _register

try:
    import cPickle as pickle
except ImportError:
    import pickle

class PickleDefault(MetaSerializer):
    """
    This serializer is based on the standard library L{pickle} module
    used with it's default protocol.
    """

    name = 'pickledefault'
    magic = b'a'
    _protocol = 0

    def dump(self, object, file):
        pickle.dump(object, file, self._protocol)

    def load(self, file):
        return pickle.load(file)

    def dumpb(self, object):
        return pickle.dumps(object, self._protocol)

    def loadb(self, b):
        assert isinstance(b, bytes)
        return pickle.loads(b)


class PickleHighest(PickleDefault):
    """
    This serializer is based on the standard libary L{pickle} modules
    used with it's highest available protocol.
    """
    name = 'picklehighest'
    magic = b'b'
    _protocol = pickle.HIGHEST_PROTOCOL

_register(PickleDefault)
_register(PickleHighest)
