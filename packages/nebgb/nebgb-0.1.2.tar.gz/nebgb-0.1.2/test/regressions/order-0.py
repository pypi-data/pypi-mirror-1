#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "HSTMPO2"
    
def test_location(rec):
    assert rec.features[1]["location"] == {
        "type": "order",
        "segments": [
            {
                "type": "reference",
                "accession": "U18266.1",
                "segment": {"type": "span", "from": 1888, "to": 2509},
            },
            {"type": "span", "from": 1, "to": 270},
            {
                "type": "reference",
                "accession": "U18268.1",
                "segment": {"type": "span", "from": 1, "to": 309},
            },
            {
                "type": "reference",
                "accession": "U18270.1",
                "segment": {"type": "span", "from": 1, "to": 6905}
            },
            {
                "type": "reference",
                "accession": "U18269.1",
                "segment": {"type": "span", "from": 1, "to": 128}
            },
            {
                "type": "reference",
                "accession": "U18271.1",
                "segment": {"type": "span", "from": 1, "to": 3234}
            }
        ]
    }
