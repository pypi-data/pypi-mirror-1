#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import datetime
import itertools
import pprint
import textwrap

import nebgb

def fmt(path, msg, rec, exp):
    return "PATH: %s\n%s\nFound:\n%s\nExpected:\n%s" % (
        path,
        msg,
        pprint.pformat(rec),
        pprint.pformat(exp)
    )

def mkpath(base, next):
    if base is None:
        return next
    return "%s.%s" % (base, next)

def sameobject(rec, exp, path=None):
    assert rec.__class__ == exp.__class__, fmt(path, "Type mismatch", rec, exp)
    func = DISPATCH[rec.__class__](rec, exp, path)

def isempty(it):
    try:
        it.next()
    except StopIteration:
        return True
    return False

def samesequence(rec, exp):
    for idx, (r, e) in enumerate(itertools.izip(rec, exp)):
        sameobject(r, e, path="%d" % idx)
    assert isempty(rec), "Record iterator is not empty."
    assert isempty(exp), "Expect iterator is not empty."        

def samebool(rec, exp, path=None):
    assert rec == exp, fmt(path, "Bool mismatch", rec, exp)

def sameint(rec, exp, path=None):
    assert rec == exp, fmt(path, "Int mismatch", rec, exp)

def samestr(rec, exp, path=None):
    assert rec == exp, fmt(path, "Str mismatch", rec, exp)

def samelist(rec, exp, path=None):
    assert len(rec) == len(exp), fmt(path, "Length mismatch", rec, exp)
    for idx, (r, e) in enumerate(zip(rec, exp)):
        sameobject(r, e, mkpath(path, "%d" % idx))

def samedict(rec, exp, path=None):
    rkeys, ekeys = list(rec.keys()), list(exp.keys())
    rkeys.sort(), ekeys.sort()
    samelist(rkeys, ekeys, mkpath(path, "__KEYS__"))
    for key in rkeys:
        sameobject(rec[key], exp[key], mkpath(path, key))

def samedate(rec, exp, path=None):
    assert rec == exp, fmt(path, "Date mismatch", rec, exp)

DISPATCH = {
    bool: samebool,
    int: sameint,
    str: samestr,
    list: samelist, 
    dict: samedict,
    datetime.date: samedate
}

def test_name(rec):
    assert rec.locus["name"] == "NM_019639"

def test_primary(rec):
    assert rec.keywords["primary"] == [
        {
            "refseq_span": {"from": 1, "to": 635},
            "primary_identifier": "CF172065.1",
            "primary_span": {"from": 1, "to": 635},
            "complement": False
        },
        {
            "refseq_span": {"from": 636, "to": 2166},
            "primary_identifier": "AC138613.6",
            "primary_span": {"from": 85778, "to": 87308},
            "complement": True
        },
        {
            "refseq_span": {"from": 2167, "to": 2424},
            "primary_identifier": "AI839133.1",
            "primary_span": {"from": 1, "to": 258},
            "complement": True
        }
    ]
