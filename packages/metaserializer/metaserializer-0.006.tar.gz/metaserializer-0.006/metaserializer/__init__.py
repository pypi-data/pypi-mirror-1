#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <25-Feb-2010 07:37:37 PST by rich@noir.com>

"""
A package which offers a simple, covering interface for a variety of
other serializers.
"""

from __future__ import unicode_literals

__docformat__ = 'epytext'

__all__ = []


# FIXME: does this need an 'implements?' predicate?

class MetaSerializer(object):
    """
    Base class for MetaSerializer objects.

    @ivar name:
    @type name: C{unicode}

    @ivar magic:
    @type magic: a C{bytes} of length 1.  This is used to identify
    upcoming serializations.  Individual serializer magic assignments
    must be unique and cannot change without destroying compatibility
    with existing serializations.  For example, any outstanding log
    files.
    """

    name = 'unknown'
    magic = b' '

    def dump(self, o, f):
        """
        Serialize an C{object} into a C{file}.

        @param object:
        @type object: C{object}

        @param file:
        @type file: C{file}
        """
        raise NotImplementedError

    def load(self, f):
        """
        Unserialize an C{object} from a C{file}.

        @param file:
        @type file: C{file}

        @return:
        @rtype: C{object}
        """
        raise NotImplementedError

    def dumpb(self, o):
        """
        Serialize an C{object} into a C{bytes}.

        @param object:
        @type object: C{object}

        @return:
        @rtype: C{bytes}
        """
        raise NotImplementedError

    def loadb(self, b):
        """
        Unserialize an C{object} from a C{bytes}.

        @param bytes:
        @type bytes: C{bytes}

        @return:
        @rtype: C{object}
        """
        raise NotImplementedError


_registry = {}

def _register(cls):
    assert cls.magic not in _registry

    _registry[cls.magic] = cls

def SerializerFromMagic(character):
    assert isinstance(character, bytes)
    assert len(character) == 1
    assert character != ' '

    return _registry[character]()
