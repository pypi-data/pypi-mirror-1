#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <23-Feb-2010 17:46:17 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into a json
serializer based on the standard libary json module, (aka,
simplejson).

@note: this serializer doesn't actually consume what it produces as a
noop.
"""

__docformat__ = 'epytext'

from metaserializer import MetaSerializer

import json

class JSON(MetaSerializer):
    """
    This serializer is based on the standard library json module, (aka, simplejson).
    """
    name = 'json'

    def dumps(self, object):
        return json.dumps(object, sort_keys=True, indent=4)

    def loads(self, string):
        return json.loads(string)
