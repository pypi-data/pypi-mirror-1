#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NM_001003918"
    
def test_primary(rec):
    assert rec.keywords["primary"] == [
        {
            "refseq_span": {"from": 1, "to": 57},
            "primary_identifier": "AC156026.3",
            "primary_span": {"from": 220162, "to": 220218},
            "complement": False
        },
        {
            "refseq_span": {"from": 58, "to": 540},
            "primary_identifier": "AF548565.1",
            "primary_span": {"from": 1, "to": 483},
            "complement": False
        },
        {
            "refseq_span": {"from": 541, "to": 1137},
            "primary_identifier": "AK135814.1",
            "primary_span": {"from": 733, "to": 1329},
            "complement": False
        },
        {
            "refseq_span": {"from": 1138, "to": 3369},
            "primary_identifier": "AF548565.1",
            "primary_span": {"from": 1081, "to": 3312},
            "complement": False
        },
        {
            "refseq_span": {"from": 3370, "to": 5427},
            "primary_identifier": "AC115005.11",
            "primary_span": {"from": 42241, "to": 44298},
            "complement": False
        }
    ]
