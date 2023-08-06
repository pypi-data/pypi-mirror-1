#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import os
import re
import types
import warnings

import t

TESTRE = re.compile(r'test')
def get_checks(idx, fname):
    modname = "regressions.%s-%d" % (fname, idx)
    try:
        mod = __import__(modname)
    except Exception, inst:
        warnings.warn("Unable to find checks for %s:\n%s" % (fname, inst))
        return
    mod = getattr(mod, "%s-%d" % (fname, idx))
    for funcname in dir(mod):
        if not TESTRE.search(funcname):
            continue
        attr = getattr(mod, funcname)
        if not isinstance(attr, types.FunctionType):
            continue
        attr.func_name = "regression.%s.%d" % (fname, idx)
        yield attr

def test_regressions():
    dirname = os.path.dirname(__file__)
    datapath = os.path.join(dirname, "data")
    for path, dnames, fnames in os.walk(datapath):
        fnames = filter(lambda x: x.endswith(".gb"), fnames)
        for fname in fnames:
            gbfname = os.path.join(path, fname)
            for idx, rec in enumerate(t.nebgb.parse_file(gbfname)):
                for check in get_checks(idx, fname[:-3]):
                    yield check, rec
        
        
        