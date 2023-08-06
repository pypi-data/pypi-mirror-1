#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "AC007323"
    
def test_counts(rec):
    assert rec.base_count == {"A": 28300, "C": 15069, "G": 15360, "T": 27707}
