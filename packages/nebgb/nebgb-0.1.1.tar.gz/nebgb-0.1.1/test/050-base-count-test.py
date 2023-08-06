#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_base_count")
def test_1():
    "BASE COUNT    28300 a  15069 c  15360 g  27707 t"
    return {"A": 28300, "C": 15069, "G": 15360, "T": 27707}

@t.parse("parse_base_count")
def test_2():
    "BASE COUNT  1311257 a2224835 c2190093 g1309889 t"
    return {"A": 1311257, "C": 2224835, "G": 2190093, "T": 1309889}
