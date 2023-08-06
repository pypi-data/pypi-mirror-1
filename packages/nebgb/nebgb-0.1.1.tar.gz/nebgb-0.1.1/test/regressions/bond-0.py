#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "SCX3_BUTOC"

def test_description(rec):
    assert rec.keywords["definition"] == "Neurotoxin III"

def test_pid(rec):
    assert rec.keywords["pid"] == "g134354"

def test_kw_length(rec):
    assert len(rec.keywords) == 9
    assert len(rec.keywords["reference"]) == 1

def test_feature_length(rec):
    assert len(rec.features) == 7
    
def test_feature_prop_lengths(rec):
    data = [2, 1, 2, 2, 2, 2, 1]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_bond_loc(rec):
    assert rec.features[2]["location"] == {
        "type": "bond",
        "positions": [12, 63]
    }

def test_site_index(rec):
    assert rec.features[6]["type"] == "Site"
    assert rec.features[6]["location"] == {
        "type": "index",
        "position": 64,
        "fuzzy": False
    }
