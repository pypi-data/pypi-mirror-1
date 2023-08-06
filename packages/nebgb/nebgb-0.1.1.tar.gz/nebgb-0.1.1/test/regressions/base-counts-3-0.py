#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NC_002678"
    
def test_counts(rec):
    assert rec.base_count == {
        "A": 1311257,
        "C": 2224835,
        "G": 2190093,
        "T": 1309889
    }
    
