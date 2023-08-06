#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "EU143250"

def test_stem_loop(rec):
    assert rec.features[6] == {
        "type": "stem_loop",
        "location": {"type": "span", "from": 3506, "to": 3595},
        "properties": {}
    }