#! /usr/bin/env python
#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the BioNEB package released
# under the MIT license.
#
"""\
BioNEB - A collection of various parsers and other odds and ends I might
end up writing.
"""

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "BioNEB",
    version = "0.3",
    description = "BioNEB - Bioinformatics utilities",
    long_description = __doc__,
    author = "Paul Joseph Davis",
    author_email = "davisp@neb.com",
    license = "MIT",
    url = "http://github.com/davisp/bioneb",
    zip_safe = False,
    
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    
    packages = [
        "bioneb",
        "bioneb.parsers"
    ],
)
