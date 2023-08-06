#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "SCX3_BUTOC"

def test_keywords(rec):
    assert rec.keywords["keywords"] == [
        "Neurotoxin",
        "Sodium channel inhibitor",
        "Amidation"
    ]