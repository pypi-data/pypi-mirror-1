#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# setup.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2005 Ben Finney
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.

"""Robust enumerated type support in Python

This package provides a class for robust enumerations in Python.

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

main_module_name = 'enum'
main_module = __import__(main_module_name)

description = __doc__.split('\n\n', 1)

setup(
    name = "enum",
    version = main_module.__version__,
    packages = find_packages(exclude=["test"]),
    package_dir = "",

    # setuptools metadata
    zip_safe = True,
    test_suite = "test.test_enum.suite",
    package_data = {
        '': ["LICENSE.*"],
    },

    # PyPI metadata
    author = main_module.__author_name__,
    author_email = main_module.__author_email__,
    description = description[0].strip(),
    license = main_module.__license__,
    keywords = "enum enumerated enumeration",
    ### url = main_module.__url__,
    long_description = description[1],
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
