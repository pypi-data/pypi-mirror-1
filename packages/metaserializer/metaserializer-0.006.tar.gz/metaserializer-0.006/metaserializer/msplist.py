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

from metaserializer import MetaSerializer

import plistlib

class plist(MetaSerializer):
    """
    This serializer is based on L{plistlib}.
    """
    name = 'plistlib'
    magic = b'f'

    def dump(self, object, file):
        plistlib.writePlist(object, file)

    def load(self, file):
        return plistlib.readPlist(file)

    def dumpb(self, object):
        return plistlib.writePlistToString(object)

    def loadb(self, b):
        assert isinstance(b, bytes)
        return plistlib.readPlistFromString(b)
