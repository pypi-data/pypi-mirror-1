#! /usr/bin/env python
#
#  Copyright 2008 New England Biolabs
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = "BioNEB",
    version = "0.2",
    description = "BioNEB - Bioinformatics utilities",
    long_description = "BioNEB - Bioinformatics utilities developed at New England Biolabs",
    author = "Paul Joseph Davis",
    author_email = "davisp@neb.com",
    license = "Apache 2.0",
    url = "http://github.com/davisp/bioneb",
    zip_safe = False,
    
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    
    install_requires = """
        httplib2
        simplejson
    """,
    
    packages = [
        "bioneb",
        "bioneb.bin",
        "bioneb.bin.couchdb",
        "bioneb.couchdb",
        "bioneb.parsers",
        "bioneb.utils"
    ],
    
    entry_points = {
        "console_scripts": [
            "bioneb-taxonomy = bioneb.bin.couchdb.taxonomy:main",
            "bioneb-genbank = bioneb.bin.couchdb.genbank:main",
        ]
    }
)
        
        
    
