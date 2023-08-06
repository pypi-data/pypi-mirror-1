#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NT_019265"
    assert rec.locus["length"] == 1250660

def test_kw_length(rec):
    assert len(rec.keywords) == 7
    assert len(rec.keywords["reference"]) == 1

def test_feature_length(rec):
    assert len(rec.features) == 5
    
def test_feature_prop_lengths(rec):
    data = [3, 4, 2, 2, 4]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_feature_variation(rec):
    assert rec.features[3] == {
        "type": "variation",
        "location": {
            "type": "index",
            "position": 217508,
            "fuzzy": False
        },
        "properties": {
            "allele": ["T", "C"],
            "db_xref": ["dbSNP:811400"]
        }
    }
