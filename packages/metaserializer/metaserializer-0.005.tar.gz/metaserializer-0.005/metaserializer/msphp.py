#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:37:37 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into a PHP serializer
based on phpserialize.

@note: This serializer can't loop back simple objects.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

from metaserializer import MetaSerializer, _register

import phpserialize

class PHP(MetaSerializer):
    """
    This serializer is based on L{phpserialize}.
    """
    name = 'phpserialize'
    magic = b'e'

    def dump(self, object, file):
        phpserialize.dump(object, file)

    def load(self, file):
        return phpserialize.load(file)

    def dumpb(self, object):
        return phpserialize.dumps(object)

    def loadb(self, b):
        assert isinstance(b, bytes)
        return phpserialize.loads(b)

_register(PHP)
