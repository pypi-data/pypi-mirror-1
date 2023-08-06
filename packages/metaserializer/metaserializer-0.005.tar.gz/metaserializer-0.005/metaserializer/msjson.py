#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:37:37 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into a json
serializer based on the standard libary json module, (aka,
simplejson).

@note: this serializer doesn't actually consume what it produces as a
noop.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

from metaserializer import MetaSerializer, _register

import json

class JSON(MetaSerializer):
    """
    This serializer is based on the standard library json module, (aka, simplejson).
    """
    name = 'json'
    magic = b'd'

    def dumpb(self, object):
        return bytes(json.dumps(object, sort_keys=True, indent=4))

    def loadb(self, b):
        assert isinstance(b, bytes)
        return json.loads(b)

_register(JSON)
