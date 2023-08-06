#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import os
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

base_dir = os.path.dirname(__file__)
long_desc = open(os.path.join(base_dir, "README.md")).read()

setup(
    name = "nebgb",
    description = "Genbank file parser.",
    long_description = long_desc,
    author = "Paul Joseph Davis",
    author_email = "davisp@neb.com",
    url = "http://github.com/davisp/nebgb",
    version = "0.1.0",
    license = "MIT",
    keywords = "bioinformatics genbank parser",
    platforms = ["any"],
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

    py_modules = ["nebgb"],

    setup_requires = ["setuptools>=0.6c8"],
    tests_require = ["nose>=0.10.0"],

    test_suite = "nose.collector"
)
