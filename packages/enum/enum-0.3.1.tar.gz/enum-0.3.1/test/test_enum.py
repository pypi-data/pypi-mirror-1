#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# test_enum.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2005 Ben Finney
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.

""" Unit test for enum module
"""

import unittest

import os
import sys
_test_dir = os.path.dirname(os.path.abspath(__file__))
_code_dir = os.path.dirname(_test_dir)
if not _code_dir in sys.path:
    sys.path.insert(1, _code_dir)

import enum


class Mock_Enum(object):
    """ Mock object for Enum testing """
    def __init__(self, *keys):
        """ Set up a new instance """
        pass

class ValuesFixture(object):
    """ Mix-in class to set up enumeration values fixture """

    def setUp(self):
        """ Set up the test fixtures """

        self.bad_keys = [ None, 0, 1, (), Mock_Enum(),
            enum.EnumValue(Mock_Enum(), 0, 'bogus'),
        ]

        self.other_values = [ None, 0, 1, (), Mock_Enum(), "bogus",
            enum.EnumValue(Mock_Enum(), 0, 'bogus'),
        ]

        self.planet_dict = dict(
            mercury = "Mercury",
            venus = "Venus",
            earth = "Earth",
            mars = "Mars",
            jupiter = "Jupiter",
            saturn = "Saturn",
            neptune = "Neptune",
            uranus = "Uranus",
            pluto = "Pluto",
        )
        planet_keys = self.planet_dict.keys()

        colour_keys = (
            'red', 'green', 'blue',
            'yellow', 'orange', 'purple',
            'white', 'black',
        )

        self.SimpleEnum = self.enum_factory_class(
            *('spam', 'eggs', 'beans')
        )

        Colour = self.enum_factory_class(*colour_keys)
        Planet = self.enum_factory_class(*planet_keys)
        self.valid_values = {
            Colour: dict(
                keys = colour_keys
            ),
            Planet: dict(
                keys = self.planet_dict.keys(),
            ),
        }

        for enumtype, params in self.valid_values.items():
            values = {}
            for i, key in enumerate(params['keys']):
                values[key] = enum.EnumValue(enumtype, i, key)
            params.update(dict(enumtype=enumtype, values=values))


class Test_Module(unittest.TestCase):
    """ Test case for the module """

    def setUp(self):
        """ Set up test fixtures """
        from sys import modules
        self.module = modules['enum']

    def test_author_name_is_string(self):
        """ Module should have __author_name__ string """
        mod_author_name = self.module.__author_name__
        self.failUnless(isinstance(mod_author_name, basestring))

    def test_author_email_is_string(self):
        """ Module should have __author_email__ string """
        mod_author_email = self.module.__author_email__
        self.failUnless(isinstance(mod_author_email, basestring))

    def test_author_is_string(self):
        """ Module should have __author__ string """
        mod_author = self.module.__author__
        self.failUnless(isinstance(mod_author, basestring))

    def test_author_contains_name(self):
        """ Module __author__ string should contain author name """
        mod_author = self.module.__author__
        mod_author_name = self.module.__author_name__
        self.failUnless(mod_author.startswith(mod_author_name))

    def test_author_contains_email(self):
        """ Module __author__ string should contain author email """
        mod_author = self.module.__author__
        mod_author_email = self.module.__author_email__
        self.failUnless(mod_author.endswith("<%s>" % mod_author_email))

    def test_date_is_string(self):
        """ Module should have __date__ string """
        mod_date = self.module.__date__
        self.failUnless(isinstance(mod_date, basestring))

    def test_copyright_is_string(self):
        """ Module should have __copyright__ string """
        mod_copyright = self.module.__copyright__
        self.failUnless(isinstance(mod_copyright, basestring))

    def test_copyright_contains_name(self):
        """ Module __copyright__ string should contain author name """
        mod_copyright = self.module.__copyright__
        mod_author_name = self.module.__author_name__
        self.failUnless(mod_copyright.endswith(mod_author_name))

    def test_copyright_contains_year(self):
        """ Module __copyright__ string should contain year """
        mod_copyright = self.module.__copyright__
        mod_year = self.module.__date__.split('-')[0]
        self.failUnless(mod_year in mod_copyright)

    def test_license_is_string(self):
        """ Module should have __license__ string """
        mod_license = self.module.__license__
        self.failUnless(isinstance(mod_license, basestring))

    def test_url_is_string(self):
        """ Module should have __url__ string """
        mod_url = self.module.__url__
        self.failUnless(isinstance(mod_url, basestring))

    def test_version_is_string(self):
        """ Module should have __version__ string """
        mod_version = self.module.__version__
        self.failUnless(isinstance(mod_version, basestring))


class Test_EnumException(unittest.TestCase):
    """ Test case for the Enum exception classes """

    def setUp(self):
        """ Set up test fixtures """
        self.valid_exceptions = {
            enum.EnumEmptyError: dict(
                min_args = 0,
                types = (enum.EnumException, AssertionError),
            ),
            enum.EnumBadKeyError: dict(
                min_args = 1,
                types = (enum.EnumException, TypeError),
            ),
            enum.EnumImmutableError: dict(
                min_args = 1,
                types = (enum.EnumException, TypeError),
            ),
            enum.EnumValueCompareError: dict(
                min_args = 2,
                types = (enum.EnumException, AssertionError),
            ),
        }

        for exc_type, params in self.valid_exceptions.items():
            args = (None,) * params['min_args']
            instance = exc_type(*args)
            self.valid_exceptions[exc_type]['instance'] = instance

    def iterate_test(self, test_func, params_dict=None):
        """ Iterate a test over a set of parameters """
        if not params_dict:
            params_dict = self.valid_exceptions
        for exc_type, params in params_dict.items():
            test_func(exc_type, params)

    def test_EnumException_abstract(self):
        """ The module exception base class should be abstract """
        self.failUnlessRaises(NotImplementedError,
            enum.EnumException
        )

    def test_exception_instance(self):
        """ Exception instance should be created """
        def test_func(exc_type, params):
            self.failUnless(params['instance'])

        self.iterate_test(test_func)

    def test_exception_types(self):
        """ Exception instances should match expected types """
        def test_func(exc_type, params):
            for match_type in params['types']:
                instance = params['instance']
                self.failUnless(isinstance(instance, match_type),
                    msg = "instance: %s, match_type: %s" % (
                        repr(instance), match_type
                    )
                )

        self.iterate_test(test_func)


class Test_EnumValue(unittest.TestCase, ValuesFixture):
    """ Test case for the EnumValue class """

    def setUp(self):
        """ Set up the test fixtures """
        self.enum_factory_class = Mock_Enum
        ValuesFixture.setUp(self)

    def iterate_test(self, test_func, datasets=None):
        """ Iterate a test function for sets of values """
        if not datasets:
            datasets = self.valid_values.keys()
        for params in [self.valid_values[s] for s in datasets]:
            for i, key in enumerate(params['keys']):
                enumtype = params['enumtype']
                value = params['values'][key]
                test_func(enumtype, i, key, value)

    def test_instantiate(self):
        """ Creating an EnumValue instance should succeed """
        def test_func(enumtype, i, key, value):
            self.failUnless(value)

        self.iterate_test(test_func)

    def test_enumtype_equal(self):
        """ EnumValue should export its enum type """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(enumtype, value.enumtype)

        self.iterate_test(test_func)

    def test_key_equal(self):
        """ EnumValue should export its string key """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(key, value.key)

        self.iterate_test(test_func)

    def test_str_key(self):
        """ String value for EnumValue should be its key string """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(key, str(value))

        self.iterate_test(test_func)

    def test_index_equal(self):
        """ EnumValue should export its sequence index """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(i, value.index)

        self.iterate_test(test_func)

    def test_repr(self):
        """ Representation of EnumValue should be meaningful """
        def test_func(enumtype, i, key, value):
            value_repr = repr(value)
            self.failUnless(value_repr.startswith('EnumValue('))
            self.failUnless(value_repr.count(repr(enumtype)))
            self.failUnless(value_repr.count(repr(i)))
            self.failUnless(value_repr.count(repr(key)))
            self.failUnless(value_repr.endswith(')'))

    def test_hash_equal(self):
        """ Each EnumValue instance should have same hash as its value """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(hash(i), hash(value))

    def test_hash_unequal(self):
        """ Different EnumValue instances should have different hashes """
        def test_func(enumtype, i, key, value):
            dataset = self.valid_values[enumtype]
            for j, other_key in enumerate(dataset['keys']):
                if i == j:
                    continue
                other_value = dataset['values'][other_key]
                self.failIfEqual(hash(value), hash(other_value))

        self.iterate_test(test_func)

    def test_cmp_equal(self):
        """ An EnumValue should compare equal to its value """
        def test_func(enumtype, i, key, value):
            self.failUnlessEqual(value,
                enum.EnumValue(enumtype, i, key)
            )

        self.iterate_test(test_func)

    def test_cmp_unequal(self):
        """ An EnumValue should compare different to other values """
        def test_func(enumtype, i, key, value):
            self.failIfEqual(value,
                enum.EnumValue(enumtype, None, None)
            )

        self.iterate_test(test_func)

    def test_cmp_sequence(self):
        """ EnumValue instances should compare as their sequence order """
        for enumtype, params in self.valid_values.items():
            for i, left_key in enumerate(params['keys']):
                for j, right_key in enumerate(params['keys']):
                    self.failUnlessEqual(cmp(i, j),
                        cmp(params['values'][left_key],
                            enum.EnumValue(enumtype, j, right_key)
                        )
                    )

    def test_cmp_unrelated_enum(self):
        """ An EnumValue should not allow comparison to other enums """
        def test_func(enumtype, i, key, value):
            self.failUnlessRaises(enum.EnumValueCompareError,
                cmp, value, enum.EnumValue(self.SimpleEnum, i, key)
            )

        self.iterate_test(test_func)

    def test_cmp_non_enum(self):
        """ An EnumValue should not allow comparison to other types """
        test_value = enum.EnumValue(self.SimpleEnum, 0, 'test')
        for other in self.other_values:
            self.failUnlessRaises(enum.EnumValueCompareError,
                cmp, test_value, other
            )

    def test_value_key(self):
        """ An EnumValue should have the specified key """
        def test_func(enumtype, i, key, instance):
            self.failUnlessEqual(key, instance.key)

        self.iterate_test(test_func)

    def test_value_enumtype(self):
        """ An EnumValue should have its associated enumtype """
        def test_func(enumtype, i, key, instance):
            self.failUnlessEqual(enumtype, instance.enumtype)

        self.iterate_test(test_func)


class Test_Enum(unittest.TestCase, ValuesFixture):
    """ Test case for the Enum class """

    def setUp(self):
        """ Set up the test fixtures """
        self.enum_factory_class = enum.Enum
        ValuesFixture.setUp(self)

    def iterate_test(self, test_func, datasets=None):
        """ Iterate a test function for sets of values """
        if not datasets:
            datasets = self.valid_values.keys()
        for enumtype, params in [(s, self.valid_values[s])
                                 for s in datasets]:
            test_func(enumtype, params)

    def test_empty_enum(self):
        """ Enum constructor should refuse empty keys sequence """
        self.failUnlessRaises(enum.EnumEmptyError,
            enum.Enum
        )

    def test_bad_key(self):
        """ Enum constructor should refuse non-string keys """
        for key in self.bad_keys:
            args = ("valid", key, "valid")
            self.failUnlessRaises(enum.EnumBadKeyError,
                enum.Enum, *args
            )

    def test_value_attributes(self):
        """ Enumeration should have attributes for each value """
        def test_func(enumtype, params):
            for i, key in enumerate(params['keys']):
                value = getattr(enumtype, key)
                test_value = enum.EnumValue(enumtype, i, key)
                self.failUnlessEqual(test_value, value)

        self.iterate_test(test_func)

    def test_length(self):
        """ Enumeration should have length of its value set """
        def test_func(enumtype, params):
            self.failUnlessEqual(len(params['values']), len(enumtype))

        self.iterate_test(test_func)

    def test_value_items(self):
        """ Enumeration should have items for each value """
        def test_func(enumtype, params):
            for i, key in enumerate(params['keys']):
                value = enumtype[i]
                test_value = enum.EnumValue(enumtype, i, key)
                self.failUnlessEqual(test_value, value)

        self.iterate_test(test_func)

    def test_iterable(self):
        """ Enumeration class should iterate over its values """
        def test_func(enumtype, params):
            for i, value in enumerate(enumtype):
                key = params['keys'][i]
                test_value = params['values'][key]
            self.failUnlessEqual(value, test_value)

        self.iterate_test(test_func)

    def test_iterate_sequence(self):
        """ Enumeration iteration should match specified sequence """
        def test_func(enumtype, params):
            values_dict = params['values']
            values_seq = [values_dict[key] for key in params['keys']]
            enum_seq = [val for val in enumtype]
            self.failUnlessEqual(values_seq, enum_seq)
            self.failIfEqual(values_seq.reverse(), enum_seq)

        self.iterate_test(test_func)

    def test_membership_bogus(self):
        """ Enumeration should not contain bogus values """
        for value in self.other_values:
            self.failIf(value in self.SimpleEnum)

    def test_membership_value(self):
        """ Enumeration should contain explicit value """
        def test_func(enumtype, params):
            for i, key in enumerate(params['keys']):
                value = params['values'][key]
                self.failUnless(value in enumtype)

        self.iterate_test(test_func)

    def test_membership_key(self):
        """ Enumeration should contain key string """
        def test_func(enumtype, params):
            for key in params['keys']:
                self.failUnless(key in enumtype)

        self.iterate_test(test_func)

    def test_add_attribute(self):
        """ Enumeration should refuse attribute addition """
        def test_func(enumtype, params):
            self.failUnlessRaises(enum.EnumImmutableError,
                setattr, enumtype, 'bogus', "bogus"
            )

        self.iterate_test(test_func)

    def test_modify_attribute(self):
        """ Enumeration should refuse attribute modification """
        def test_func(enumtype, params):
            for key in params['keys']:
                self.failUnlessRaises(enum.EnumImmutableError,
                    setattr, enumtype, key, "bogus"
                )

        self.iterate_test(test_func)

    def test_delete_attribute(self):
        """ Enumeration should refuse attribute deletion """
        def test_func(enumtype, params):
            for key in params['keys']:
                self.failUnlessRaises(enum.EnumImmutableError,
                    delattr, enumtype, key
                )

        self.iterate_test(test_func)

    def test_add_item(self):
        """ Enumeration should refuse item addition """
        def test_func(enumtype, params):
            index = len(params['keys'])
            self.failUnlessRaises(enum.EnumImmutableError,
                enumtype.__setitem__, index, "bogus"
            )

        self.iterate_test(test_func)

    def test_modify_item(self):
        """ Enumeration should refuse item modification """
        def test_func(enumtype, params):
            for i, key in enumerate(params['keys']):
                self.failUnlessRaises(enum.EnumImmutableError,
                    enumtype.__setitem__, i, "bogus"
                )

        self.iterate_test(test_func)

    def test_delete_item(self):
        """ Enumeration should refuse item deletion """
        def test_func(enumtype, params):
            for i, key in enumerate(params['keys']):
                self.failUnlessRaises(enum.EnumImmutableError,
                    enumtype.__delitem__, i
                )

        self.iterate_test(test_func)


def suite():
    """ Create the test suite for this module """
    from sys import modules
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(modules[__name__])
    return suite


def __main__(argv=None):
    """ Mainline function for this module """
    import sys as _sys
    if not argv:
        argv = _sys.argv

    exitcode = None
    try:
        unittest.main(argv=argv, defaultTest='suite')
    except SystemExit, e:
        exitcode = e.code

    return exitcode

if __name__ == '__main__':
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
