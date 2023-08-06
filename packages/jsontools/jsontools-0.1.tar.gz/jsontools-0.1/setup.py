#! /usr/bin/env python
"""jsontools - Useful utilities for JSON

This package implements a couple useful utilities for
working in json.

1. JSON diff/apply combination that can be used to create
and apply edit scripts for JSON data.

2. JSON fuzzy generator/modifier provide generation of
fuzzy data for JSON.

3. JSON comparison utilities because floats can get chopped
durring serialization leading to representation errors.
"""

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

setup(
    name = "jsontools",
    version = "0.1",
    description = __doc__.split('\n')[0],
    long_description = __doc__,
    author = "Paul Joseph Davis",
    author_email = "paul.joseph.davis@gmail.com",
    license = "MIT",
    url = "http://www.davispj.com/svn/projects/jsontools",
    platforms = ["any"],
    zip_safe = True,

    classifiers = filter(None, classifiers.split('\n')),
    
    requires = ["simplejson"],
    
    packages = [
        "jsontools"
    ]
)
