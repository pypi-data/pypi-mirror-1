#!/usr/bin/python -tt
# -*- coding: UTF-8 -*-
# vim: sw=4 ts=4 et:

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.1.1"

setup(name = "minitestlib",
    description = "Library to handle TET journal files",
    version = version,
    author = "Andy Shevchenko",
    author_email = "andy.shevchenko@gmail.com",
    packages = ['minitestlib'],
    long_description = "Python library to parse and analyze TET journal files",
    keywords = "python test TET",
    platforms = "Python 2.3 and later",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Operating System :: Unix",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ]
    )
