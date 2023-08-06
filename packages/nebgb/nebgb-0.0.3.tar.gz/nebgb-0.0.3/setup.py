#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

"""
Usage:

    >>> import nebgb
    >>> rec = nebgb.parse_file("./test/data/simple-1.gb").next()
    >>> rec.locus["name"]
    'NP_034640'
    >>> rec.locus["length"]
    182
    >>> rec.keywords["source"]["name"]
    'house mouse'
    >>> rec.features[1]["properties"]["product"]
    'interferon beta, fibroblast'
    >>> for seq in rec.seqiter:
    ...    print seq
    mnnrwilhaafllcfsttalsinykqlqlqertnirkcqelleqlngkinltyradfkip
    memtekmqksytafaiqemlqnvflvfrnnfsstgwnetivvrlldelhqqtvflktvle
    ekqeerltwemsstalhlksyywrvqrylklmkynsyawmvvraeifrnfliirrltrnf
    qn


Alternatively you can use `nebgb.parse()` to parse a string or iterator that
yields lines of a Genbank file.
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(
    name = "nebgb",
    description = "Genbank file parser.",
    long_description = __doc__,
    author = "Paul Joseph Davis",
    author_email = "davisp@neb.com",
    url = "http://github.com/davisp/nebgb",
    version = "0.0.3",
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
