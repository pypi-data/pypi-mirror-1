#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NM_006141"
    
def test_counts(rec):
    assert rec.base_count == {"A": 474, "C": 356, "G": 428, "T": 364}
