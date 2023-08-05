#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# setup.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2005 Ben Finney
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.

"""This package provides a class for robust enumerations in Python.

An enumeration object is created with a sequence of string
arguments to the Enum() function::

    >>> from enum import Enum
    >>> Colours = Enum('red', 'blue', 'green')
    >>> Weekdays = Enum('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

The return value is an immutable sequence object with a value for each
of the string arguments. Each value is also available as an attribute
named from the corresponding string argument::

    >>> pizza_night = Weekdays[4]
    >>> pixel_colour = Colours.blue

The values are constants that can be compared only with other values
from the same enumeration, but can be coerced to simple strings
matching the original arguments to Enum().

The design is based in part on Zoran Isailovski's recipe, "First
Class Enums in Python" in the ASPN Python Cookbook
<URL:http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413486>.
"""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

from sys import modules

setup(
    name = "enum",
    version = "0.3",
    py_modules = ['enum'],

    # setuptools metadata
    zip_safe = True,
    test_suite = "test.test_enum.suite",

    # PyPI metadata
    author = "Ben Finney",
    author_email = "ben+python@benfinney.id.au",
    description = "Robust enumerated data types in Python",
    license = "Choice of GPL or Python license",
    keywords = "enum enumerated enumeration",
    ### url = "http://example.org/projects/enum/",
    long_description = modules[__name__].__doc__,
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
