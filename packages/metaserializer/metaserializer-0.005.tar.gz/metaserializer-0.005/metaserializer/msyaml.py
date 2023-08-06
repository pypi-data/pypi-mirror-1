#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:42:21 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into a yaml
serializer based on PyYAML.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

from metaserializer import MetaSerializer, _register

import yaml
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class YAML(MetaSerializer):
    """
    This serializer is based on U{PyYAML<http://pypi.python.org/pypi/PyYAML>}.
    """
    name = 'yaml'
    magic = b'c'

    def dump(self, object, file):
        yaml.dump(object, file, Dumper=Dumper)

    def load(self, file):
        return yaml.load(file, Loader=Loader)

    def dumpb(self, object):
        return bytes(yaml.dump(object, Dumper=Dumper))

    def loadb(self, b):
        return yaml.load(b, Loader=Loader)

_register(YAML)
