#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <23-Feb-2010 17:18:50 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into two distinct
subclasses both of which are based on the pickle module from the
standard library.
"""

__docformat__ = 'epytext'

from metaserializer import MetaSerializer

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
    _protocol = 0

    def dump(self, object, file):
        pickle.dump(object, file, self._protocol)

    def load(self, file):
        return pickle.load(file)

    def dumps(self, object):
        return pickle.dumps(object, self._protocol)

    def loads(self, string):
        return pickle.loads(string)


class PickleHighest(PickleDefault):
    """
    This serializer is based on the standard libary L{pickle} modules
    used with it's highest available protocol.
    """
    name = 'picklehighest'
    _protocol = pickle.HIGHEST_PROTOCOL
