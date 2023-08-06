#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "HUGLUT1"
    
def test_counts(rec):
    assert rec.base_count == {"A": 206, "C": 172, "G": 195, "T": 168}
