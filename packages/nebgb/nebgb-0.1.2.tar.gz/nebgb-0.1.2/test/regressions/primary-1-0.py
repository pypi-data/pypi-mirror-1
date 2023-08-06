#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NM_015658"

def test_primary(rec):
    assert rec.keywords["primary"] == [
        {
            "refseq_span": {"from": 1, "to": 27},
            "primary_identifier": "DA002961.1",
            "primary_span": {"from": 1, "to": 27},
            "complement": False
        },
        {
            "refseq_span": {"from": 28, "to": 976},
            "primary_identifier": "BC003555.1",
            "primary_span": {"from": 1, "to": 949},
            "complement": False
        },
        {
            "refseq_span": {"from": 977, "to": 984},
            "primary_identifier": "AW749585.1",
            "primary_span": {"from": 25, "to": 32},
            "complement": False
        },
        {
            "refseq_span": {"from": 985, "to": 1901},
            "primary_identifier": "BC003555.1",
            "primary_span": {"from": 958, "to": 1874},
            "complement": False
        },
        {
            "refseq_span": {"from": 1902, "to": 2301},
            "primary_identifier": "AK225239.1",
            "primary_span": {"from": 1857, "to": 2256},
            "complement": False
        },
        {
            "refseq_span": {"from": 2302, "to": 2695},
            "primary_identifier": "BC003555.1",
            "primary_span": {"from": 2275, "to": 2668},
            "complement": False
        },
        {
            "refseq_span": {"from": 2696, "to": 2789},
            "primary_identifier": "BX645732.1",
            "primary_span": {"from": 174, "to": 267},
            "complement": False
        },
        {
            "refseq_span": {"from": 2790, "to": 2817},
            "primary_identifier": "AK225239.1",
            "primary_span": {"from": 2739, "to": 2766},
            "complement": False
        }
    ]
