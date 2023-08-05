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

__author_name__ = "Ben Finney"
__author_email__ = "ben+python@benfinney.id.au"
__author__ = "%s <%s>" % (__author_name__, __author_email__)
__date__ = "2005-11-29"
__copyright__ = "Copyright © %s %s" % (
    __date__.split('-')[0], __author_name__
)
__license__ = "Choice of GPL or Python license"
__url__ = "http://bignose.whitetree.org/projects/enum/"
__version__ = "0.3.1"

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

class EnumImmutableError(TypeError, EnumException):
    """ Raised when attempting to modify an Enum """

    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return "Enumeration does not allow modification"

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

    def __init__(self, enumtype, index, key):
        """ Set up a new instance """
        self.__enumtype = enumtype
        self.__index = index
        self.__key = key

    def __get_enumtype(self):
        return self.__enumtype
    enumtype = property(__get_enumtype)

    def __get_key(self):
        return self.__key
    key = property(__get_key)

    def __str__(self):
        return "%s" % (self.key)

    def __get_index(self):
        return self.__index
    index = property(__get_index)

    def __repr__(self):
        return "EnumValue(%s, %s, %s)" % (
            repr(self.__enumtype),
            repr(self.__index),
            repr(self.__key),
        )

    def __hash__(self):
        return hash(self.__index)

    def __cmp__(self, other):
        self_type = self.enumtype
        try:
            assert self_type == other.enumtype
        except (AssertionError, AttributeError):
            raise EnumValueCompareError(self, other)

        return cmp(self.index, other.index)


class Enum(object):
    """ Enumerated type """

    def __init__(self, *keys, **kwargs):
        """ Create an enumeration instance """

        value_type = kwargs.get('value_type', EnumValue)

        if not keys:
            raise EnumEmptyError()

        keys = tuple(keys)
        values = [None] * len(keys)

        for i, key in enumerate(keys):
            value = value_type(self, i, key)
            values[i] = value
            try:
                super(Enum, self).__setattr__(key, value)
            except TypeError, e:
                raise EnumBadKeyError(key)

        super(Enum, self).__setattr__('_keys', keys)
        super(Enum, self).__setattr__('_values', values)

    def __setattr__(self, name, value):
        raise EnumImmutableError(name)

    def __delattr__(self, name):
        raise EnumImmutableError(name)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def __setitem__(self, index, value):
        raise EnumImmutableError(index)

    def __delitem__(self, index):
        raise EnumImmutableError(index)

    def __iter__(self):
        return iter(self._values)

    def __contains__(self, value):
        is_member = False
        if isinstance(value, basestring):
            is_member = (value in self._keys)
        else:
            try:
                is_member = (value in self._values)
            except EnumValueCompareError, e:
                is_member = False
        return is_member
