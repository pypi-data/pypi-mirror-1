#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_locus")
def test_1():
    """
LOCUS       DMBR25B3   154329 bp    DNA             INV       07-FEB-2000
    """
    return {
        'name': 'DMBR25B3',
        'length': 154329,
        'base_type': 'bp',
        'molecule_type': 'DNA',
        'division': 'INV',
        'date': t.datetime.date(2000, 2, 7)
    }

@t.parse("parse_locus")
def test_2():
    """
LOCUS       EU032008                1005 bp    RNA     linear   VRL 30-SEP-2007    
    """
    return {
        "name": "EU032008",
        "length": 1005,
        "base_type": "bp",
        "molecule_type": "RNA",
        "topology": "linear",
        "division": "VRL",
        "date": t.datetime.date(2007, 9, 30)
    }
    
@t.parse("parse_locus")
def test_3():
    """
LOCUS       NM_015658               2817 bp    mRNA    linear   PRI 27-SEP-2007
    """
    return {
        'name': 'NM_015658',
        'length': 2817,
        'base_type': 'bp',
        'molecule_type': 'mRNA',
        'topology': 'linear',
        'division': 'PRI',
        'date': t.datetime.date(2007, 9, 27)
    }
    
@t.parse("parse_locus")
def test_4():
    """
LOCUS       SCX3_BUTOC                64 aa            linear   INV 16-OCT-2001
    """
    return {
        'name': 'SCX3_BUTOC',
        'length': 64,
        'base_type': 'aa',
        'topology': 'linear',
        'division': 'INV',
        'date': t.datetime.date(2001, 10, 16),
    }
