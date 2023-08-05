# -*- encoding: utf-8 -*-

# enum.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2005 Ben Finney
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.

""" Enumerated type implementation
"""

from sets import Set as set


class EnumException(Exception):
    """ Base class for all exceptions in this module """
    def __init__(self):
        if self.__class__ is EnumException:
            raise NotImplementedError, \
                "%s is an abstract class for subclassing" % self.__class__

class EnumEmptyError(AssertionError, EnumException):
    """ Raised when attempting to create an empty enumeration """

    def __str__(self):
        return "Enumerations cannot be empty"

class EnumBadKeyError(TypeError, EnumException):
    """ Raised when creating an Enum with non-string keys """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Enumeration keys must be strings: %s" % (self.key,)

class EnumValueCompareError(AssertionError, EnumException):
    """ Raised when comparing EnumValues of different enumerations """

    def __init__(self, left, right):
        """ Set up a new instance """
        self.__left = left
        self.__right = right

    def __str__(self):
        values = (self.__left, self.__right)
        return "Not values from the same enumeration: %s" % str(values)


class EnumValue(object):
    """ A specific value of an enumerated type """

    def __init__(self, enumtype, key, value):
        """ Create the enumeration value """
        self.__enumtype = enumtype
        self.__key = key
        self.__value = value

    def __get_enumtype(self):
        return self.__enumtype
    enumtype = property(__get_enumtype)

    def __get_key(self):
        return self.__key
    key = property(__get_key)

    def __str__(self):
        return "%s" % (self.key)

    def __repr__(self):
        return "EnumValue(%s, %s, %s)" % (
            repr(self.__enumtype),
            repr(self.__key),
            repr(self.__value),
        )

    def __hash__(self):
        return hash(self.__value)

    def __cmp__(self, other):
        self_type = self.enumtype
        try:
            assert self_type == other.enumtype
        except (AssertionError, AttributeError):
            raise EnumValueCompareError(self, other)

        return cmp(self.__value, other.__value)


class Enum(object):
    """ Enumerated type """

    def __init__(self, *keys, **kwargs):
        """ Create an enumeration instance """

        value_type = kwargs.get('value_type', EnumValue)

        if not keys:
            raise EnumEmptyError()

        self.__keys = set(keys)
        self.__values = [None] * len(keys)

        for i, key in enumerate(keys):
            value = value_type(self, key, i)
            self.__values[i] = value
            try:
                setattr(self, key, value)
            except TypeError, e:
                raise EnumBadKeyError(key)

    def __len__(self):
        return len(self.__values)

    def __iter__(self):
        return iter(self.__values)

    def __contains__(self, value):
        is_member = False
        if isinstance(value, basestring):
            is_member = (value in self.__keys)
        else:
            try:
                is_member = (value in self.__values)
            except EnumValueCompareError, e:
                is_member = False
        return is_member
