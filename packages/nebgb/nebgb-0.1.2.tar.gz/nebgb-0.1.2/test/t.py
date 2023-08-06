#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import datetime
import itertools
import pprint
import textwrap
import types

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

def bothnone(rec, exp, path=None):
    assert rec is None and exp is None, fmt(path, "None mistmatch", rec, exp)

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
    types.NoneType: bothnone,
    bool: samebool,
    int: sameint,
    str: samestr,
    list: samelist,
    tuple: samelist, 
    dict: samedict,
    datetime.date: samedate
}


class parse(object):
    def __init__(self, name):
        self.name = name
    def __call__(self, func):
        def wrap(*args, **kwargs):
            data = self.prep(func.func_doc)
            result = getattr(nebgb, self.name)(data)
            sameobject(result, func())
        wrap.func_name = func.func_name
        return wrap
    def prep(self, data):
        return data.lstrip("\n").rstrip(" ")


def normalize(data):
    return ' '.join(data.split())

def dedent(data, left=None, right=None):
    return textwrap.dedent(data.lstrip(left).rstrip(right))