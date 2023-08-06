#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_location")
def test_index_1():
    "123"
    return {"position": 123, "fuzzy": False, "type": "index"}

@t.parse("parse_location")
def test_index_2():
    "<34"
    return {"position": 34, "fuzzy": True, "type": "index"}

@t.parse("parse_location")
def test_index_3():
    ">935345"
    return {"position": 935345, "fuzzy": True, "type": "index"}

@t.parse("parse_location")
def test_bond():
    "bond(1,5)"
    return {"type": "bond", "positions": [1, 5]}

@t.parse("parse_location")
def test_one_of():
    "one-of(89,453)"
    return {"type": "one-of", "positions": [89, 453]}

@t.parse("parse_location")
def test_span_1():
    "1..30"
    return {"type": "span", "from": 1, "to": 30}

@t.parse("parse_location")
def test_span_2():
    "<1..>45"
    return {
        "type": "span",
        "from": 1,
        "to": 45,
        "modifiers": {"from": "fuzzy", "to": "fuzzy"}
    }

@t.parse("parse_location")
def test_span_3():
    "one-of(8,9)..56"
    return {
        "type": "span",
        "from": {"type": "one-of", "positions": [8, 9]},
        "to": 56
    }

@t.parse("parse_location")
def test_site():
    "45^46"
    return {
        "type": "site",
        "between": [
            {"type": "index", "position": 45, "fuzzy": False},
            {"type": "index", "position": 46, "fuzzy": False}
        ]
    }

@t.parse("parse_location")
def test_choice():
    "90.414"
    return {
        "type": "choice",
        "between": [
            {"type": "index", "position": 90, "fuzzy": False},
            {"type": "index", "position": 414, "fuzzy": False}
        ]
    }

@t.parse("parse_location")
def test_gap():
    "gap(100)"
    return {"type": "gap", "length": 100}

@t.parse("parse_location")
def test_join_1():
    "join(5..10,25..45)"
    return {
        "type": "join",
        "segments": [
            {"type": "span", "from": 5, "to": 10},
            {"type": "span", "from": 25, "to": 45}
        ]
    }

@t.parse("parse_location")
def test_join_2():
    "join(14..24,complement(56..34))"
    return {
        "type": "join",
        "segments": [
            {"type": "span", "from": 14, "to": 24},
            {
                "type": "complement",
                "segment": {"type": "span", "from": 56, "to": 34}
            }
        ]
    }

@t.parse("parse_location")
def test_complement_1():
    "complement(15..34)"
    return {
        "type": "complement",
        "segment": {"type": "span", "from": 15, "to": 34}
    }

@t.parse("parse_location")
def test_complement_2():
    "complement(join(45..90,100..102))"
    return {
        "type": "complement",
        "segment": {
            "type": "join",
            "segments": [
                {"type": "span", "from": 45, "to": 90},
                {"type": "span", "from": 100, "to": 102}
            ]
        }
    }

@t.parse("parse_location")
def test_order():
    "order(4..5,9..10)"
    return {
        "type": "order",
        "segments": [
            {"type": "span", "from": 4, "to": 5},
            {"type": "span", "from": 9, "to": 10}
        ]
    }

@t.parse("parse_location")
def test_reference():
    "NC_001912.5:5..9"
    return {
        "type": "reference",
        "accession": "NC_001912.5",
        "segment": {"type": "span", "from": 5, "to": 9}
    }

