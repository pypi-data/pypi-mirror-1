#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "EU071348"

def test_feature_length(rec):
    assert len(rec.features) == 3

def test_fuzzy_from(rec):
    assert rec.features[1]["location"] == {
        "type": "span",
        "from": 1,
        "to": 51,
        "modifiers": {"from": "fuzzy"}
    }

def test_fuzzy_to(rec):
    assert rec.features[2]["location"] == {
        "type": "span",
        "from": 52,
        "to": 705,
        "modifiers": {"to": "fuzzy"}
    }