#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "HSTMPO2"
    
def test_segment(rec):
    assert rec.keywords["segment"] == {"position": 2, "of": 6}