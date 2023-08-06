#!/usr/bin/env python -3
# -*- coding: utf-8 -*-
#
# Copyright 2010 K. Richard Pixley.
# See LICENSE for details.
#
# Time-stamp: <23-Feb-2010 13:29:05 PST by rich@noir.com>

"""
A package which offers a simple, covering interface for a variety of other serializers.
"""

__docformat__ = 'epytext'

__all__ = []


# FIXME: does this need an 'implements?' predicate?

class MetaSerializer(object):
    """
    Base class for MetaSerializer objects.

    @ivar name:
    @type name: C{str}
    """

    name = 'unknown'

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

    def dumps(self, o):
        """
        Serialize an C{object} into a C{str}.

        @param object:
        @type object: C{object}

        @return:
        @rtype: C{str}
        """
        raise NotImplementedError

    def loads(self, s):
        """
        Unserialize an C{object} from a C{str}.

        @param string:
        @type string: C{str}

        @return:
        @rtype: C{object}
        """
        raise NotImplementedError
