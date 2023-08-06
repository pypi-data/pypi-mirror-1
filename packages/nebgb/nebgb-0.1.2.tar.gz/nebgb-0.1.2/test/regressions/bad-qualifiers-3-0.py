#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "EU032008"

def test_kw_length(rec):
    assert len(rec.keywords) == 6
    assert len(rec.keywords["reference"]) == 2

def test_feature_length(rec):
    assert len(rec.features) == 3
    
def test_feature_prop_lengths(rec):
    data = [8, 1, 7]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_first_bad_qual(rec):
    assert rec.features[0]["properties"]["virion"] == True
