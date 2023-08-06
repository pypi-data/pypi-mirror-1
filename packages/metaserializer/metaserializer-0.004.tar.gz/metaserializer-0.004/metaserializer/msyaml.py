#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <23-Feb-2010 17:37:00 PST by rich@noir.com>

"""
This module subclasses the MetaSerializer object into a yaml
serializer based on PyYAML.
"""

__docformat__ = 'epytext'

from metaserializer import MetaSerializer

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

    def dump(self, object, file):
        yaml.dump(object, file, Dumper=Dumper)

    def load(self, file):
        return yaml.load(file, Loader=Loader)

    def dumps(self, object):
        return yaml.dump(object, Dumper=Dumper)

    def loads(self, string):
        return yaml.load(string, Loader=Loader)
