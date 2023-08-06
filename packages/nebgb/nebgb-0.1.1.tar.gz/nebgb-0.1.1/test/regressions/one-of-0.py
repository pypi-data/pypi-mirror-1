#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "HSTMPO1"
    
def test_one_of(rec):
    assert rec.features[3]["location"] == {
        "type": "span",
        "from": {
            "type": "one-of",
            "positions": [1888, 1901]
        },
        "to": 2479
    }