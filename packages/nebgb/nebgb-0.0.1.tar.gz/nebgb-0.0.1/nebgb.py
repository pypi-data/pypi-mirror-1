#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import calendar
import datetime
import itertools
import sys
import types
import warnings

from pyparsing import *

__all__ = ["Record", "Sequence", "parse", "parse_file"]

#
# Constants
#

STRANDS = "ss ds ms".split()
MOL_TYPES = """NS DNA RNA tRNA rRNA mRNA uRNA snRNA snoRNA""".split()
TOPOLOGY = "linear circular".split()
DIVISIONS = """
    PRI ROD MAM VRT INV PLN BCT VRL PHG SYN UNA EST PAT STS GSS HTG HTC ENV CON
""".split()
MONTHS = dict(
    (m.upper(), i) for i, m in enumerate(calendar.month_abbr) if m
)
MULTI_KEYWORDS = set(["reference"])

#
# Parse Actions
#

def to_int(t):
    return int(t[0])

def to_month(s, l, t):
    global MONTHS
    if t[0].upper() not in MONTHS:
        raise ParseException(s, len(s), "Expected a month abbreviation.")
    return MONTHS[t[0].upper()]

def to_date(s, l, t):
    day = t[0][0]
    month = t[0][1]
    year = t[0][2]
    return datetime.date(year, month, day)

#
# Grammar Definition
#

# General
integer = Word(nums).setParseAction(to_int)
normalized = Combine(
    ZeroOrMore(Word(printables)), joinString=" ", adjacent=False
)
ddline = White(min=0).suppress() + restOfLine + LineEnd()
dedented = Combine(OneOrMore(ddline))
norm_inlinewhite = OneOrMore(" \t").setParseAction(replaceWith(" "))
sup_hyphen = Suppress("-")
sup_colon = Suppress(":")
sup_semicolon = Suppress(";")
matchall = Regex("(.|\n)*")

accession = Word(alphas, bodyChars=alphanums + "_")
gi = Suppress("GI:") + Word(nums)

# Locus Parsing
name = Word(printables)("name")
length = Word(nums)("length").setParseAction(to_int)
base_type = (Literal("bp") ^ Literal("aa"))("base_type")
strandedness = Optional(Or(map(Literal, STRANDS)))("strandedness")
mol_type = Optional(Or(map(Literal, MOL_TYPES)))("molecule_type")
topology = Optional(Or(map(Literal, TOPOLOGY)))("topology")
division = Or(map(Literal, DIVISIONS))("division")
day = Word(nums, exact=2).setParseAction(to_int)("day")
month = Word(alphas, exact=3).setParseAction(to_month)("month")
year = Word("12", bodyChars=nums, exact=4).setParseAction(to_int)("year")
date = Group(day + sup_hyphen + month + sup_hyphen + year)("date")
date = date.setParseAction(to_date)
locus = LineStart() + Literal("LOCUS").suppress() + name + length \
        + base_type + strandedness + mol_type + topology + division + date

# Keyword Parsing
firstline = WordStart() + restOfLine + LineEnd()
continuation = White() + firstline
keywordname = Word(alphas + "_") + White()
keyword = Combine(
    keywordname + firstline + ZeroOrMore(continuation), adjacent=False
)
keywordsection = OneOrMore(keyword)

optspace = Optional(" ").suppress()
keywordfirst = ZeroOrMore(Word(printables) + optspace) + LineEnd().suppress()
keywordcont = White(exact=12).suppress() + keywordfirst
keywordnorm = Combine(keywordfirst + ZeroOrMore(keywordcont), joinString=" ")

# DEFINITION
definition = Literal("DEFINITION").suppress() + normalized

# ACCESSION
accfirst = accession.setResultsName("first")
acclast = accession.setResultsName("last")
accrange = Group(accfirst + Suppress("-") + acclast)
accession = Literal("ACCESSION").suppress() + OneOrMore(accrange ^ accession)

# VERSION
veracc = Combine(
    Word(alphanums + "_") + Optional("." + Word(nums))("accession")
)
version = Literal("VERSION").suppress() + veracc + gi

# PID
pid = Literal("PID").suppress() + Word(alphanums)

# DBSOURCE
dbsource = Literal("DBSOURCE").suppress() + dedented

# DBLINK
dbln_type = Or(map(Literal, ["Project", "Trace Assembly Archive"]))("type")
dbln_type = dbln_type.setParseAction(lambda t: t[0].lower())
dbln_list = Group(delimitedList(Word(alphanums + "_")))("identifiers")
dblink = Group(dbln_type + sup_colon + dbln_list)("dblink")

# KEYWORDS
kwphrase = ZeroOrMore(Word(''.join(p for p in printables if p != ";")))
kwphrase = Combine(kwphrase, joinString=" ", adjacent=False)
kwphrases = delimitedList(kwphrase, delim=";")
kwempty = Suppress("." + LineEnd())
keywords = Literal("KEYWORDS").suppress() + (kwempty | kwphrases)

# SEGMENT
segment = Literal("SEGMENT").suppress() \
            + integer("position") + Suppress("of") + integer("total")

# SOURCE
sourcename = Literal("SOURCE").suppress() + keywordnorm
organism = Literal("ORGANISM").suppress() + Combine(WordStart() + restOfLine)
taxname = Combine(OneOrMore(
    Word(filter(lambda p: p != ";", printables)) + Suppress(Optional(" "))
), joinString=" ", adjacent=True)
taxonomy = delimitedList(OneOrMore(taxname), delim=";")
source = sourcename + organism + taxonomy

# REFERENCE
basesorresidues = Suppress("bases") | Suppress("residues")
position = basesorresidues + integer("from") + Suppress("to") + integer("to")
notes = Word(''.join(p for p in printables if p not in "()"))("notes")
refloc = Suppress("(") + Optional(position) + Optional(notes) + Suppress(")")
refdesc = integer("refid") + Group(refloc)
authors = Group(Literal("AUTHORS") + keywordnorm)
title = Group(Literal("TITLE") + keywordnorm)
journal = Group(Literal("JOURNAL") + keywordnorm)
medline = Group(Literal("MEDLINE") + Word(nums, exact=8)("medline"))
pubmed = Group(Literal("PUBMED") + Word(nums)("pubmed"))
remark = Group(Literal("REMARK") + keywordnorm)
refsubs = OneOrMore(authors ^ title ^ journal ^ medline ^ pubmed ^ remark)
reference = Literal("REFERENCE").suppress() + refdesc + refsubs

# PRIMARY
priheaderliterals = "REFSEQ_SPAN PRIMARY_IDENTIFIER PRIMARY_SPAN COMP".split()
priheader = And(map(Literal, priheaderliterals)).suppress()
pri_span = Group(integer("from") + Suppress("-") + integer("to"))
pri_row = Group(pri_span + veracc + pri_span + Optional("c"))
primary = Literal("PRIMARY").suppress() + priheader + OneOrMore(pri_row)

# COMMENT
comment = Literal("COMMENT").suppress() + dedented

# LOCATION
location = Forward()
args = (Suppress("(") + delimitedList(location) + Suppress(")"))
index = Group(Optional(Word("<>", exact=1)) + integer)
intargs = (Suppress("(") + delimitedList(integer) + Suppress(")"))
bond = Group(Literal("bond") + intargs)("bond")
one_of = Group(Literal("one-of") + intargs)("one-of")
position = index | one_of
span = Group(position + Suppress("..") + position)
site = Group(index + Suppress("^") + index)
choice = Group(index + Suppress(".") + index)
gap = Group(Literal("gap") + Suppress("(") + integer + Suppress(")"))
complement = Group(Literal("complement") + args)
join = Group(Literal("join") + args)("join")
order = Group(Literal("order") + args)("order")
referenceloc = Group(veracc + Suppress(":") + location)("reference")
location << (
    complement | join | order | bond | gap | referenceloc \
        | span | site | choice | index | one_of
)

# FEATURES
featcont = White(exact=21).suppress() + restOfLine + LineEnd()
feature = Combine(
    White(exact=5).suppress() + restOfLine + LineEnd() + ZeroOrMore(featcont),
    adjacent=False
)
featuresection = OneOrMore(feature)

featname = Word(alphanums + "_'")
featlocword = Word(''.join(filter(lambda p: p != "/", printables)))
featloc = Combine(OneOrMore(featlocword), adjacent=False)
qualname = Word(''.join(filter(lambda p: p != "=", printables)))
qualquoted = Combine(
    Suppress('"') + Regex(r'[^"]*') + Suppress('"'),
    adjacent=True
)
qualunquoted = Word(filter(lambda p: p != '"', printables))
qualvalue = Suppress("=") + (qualquoted | qualunquoted) + LineEnd().suppress()
qualnovalue = LineEnd().suppress()
qualifier = Group(Suppress("/") + qualname + (qualvalue | qualnovalue))
featgroup = featname + featloc + ZeroOrMore(qualifier)

# CONTIG
contig = Literal("CONTIG") + location

# BASE COUNT
single_count = Group(integer + Word(alphas))
base_count = Literal("BASE COUNT") + OneOrMore(single_count)


#
# Keyword Parsers
#

def _k_definition(data):
    return definition.parseString(data)[0].rstrip(".")

def _k_accession(data):
    res = accession.parseString(data)
    ret = {"primary": res[0], "secondary": []}
    for acc in res[1:]:
        if hasattr(acc, "first"):
            ret["secondary"].append({"first": acc.first, "last": acc.last})
        else:
            ret["secondary"].append(acc)
    return ret

def _k_version(data):
    res = version.parseString(data)
    return {"accession": res[0], "gi": res[1]}

def _k_pid(data):
    return pid.parseString(data)[0]

def _k_dbsource(data):
    return dbsource.parseString(data)[0].strip()

def _k_segment(data):
    res = segment.parseString(data)
    return {"position": res.position, "of": res.total}

def _k_keywords(data):
    res = keywords.parseString(data)
    return [kw.rstrip(".") for kw in res]

def _k_source(data):
    res = source.parseString(data)
    ret = {"name": res[0].rstrip(".")}
    if len(res) > 1:
        ret["organism"] = res[1]
        ret["taxonomy"] = [r.rstrip(".") for r in res[2:]]
    return ret

def _k_reference(data):
    res = reference.parseString(data)
    loc = {
        "from": getattr(res[1], "from", None),
        "to": getattr(res[1], "to", None)
    }
    ref = {
        "refid": res[0],
        "location": loc,
        "notes": getattr(res[1], "notes", "")
    }
    for r in res[2:]:
        if r[0].lower() in ref:
            raise ParseException(data, len(data), "Repeated subkeyword.")
        ref[r[0].lower()] = r[1]
    return ref

def _k_primary(data):
    res = primary.parseString(data.strip())
    ret = []
    for row in res:
        if len(row) < 3 or len(row) > 4:
            raise ParseException(data, len(data), "Invalid PRIMARY row.")
        ret.append({
            "refseq_span": {"from": row[0]["from"], "to": row[0]["to"]},
            "primary_identifier": row[1],
            "primary_span": {"from": row[2]["from"], "to": row[2]["to"]},
            "complement": (len(row) == 4 and row[3] == "c")
        })
    return ret

def _k_comment(data):
    return comment.parseString(data)[0].strip()



#
# Location Parsers
#

def _l_index(t):
    return {
        "type": "index",
        "position": t[0][-1],
        "fuzzy": str(t[0][0]) in "<>"
    }

def _l_bond(t):
    return {
        "type": "bond",
        "positions": t[0][1:]
    }

def _l_one_of(t):
    return {
        "type": "one-of",
        "positions": t[0][1:]
    }

def _l_span(t):
    if t[0][0]["type"] == "index":
        fr = t[0][0]["position"]
    else:
        fr = t[0][0]
    if t[0][1]["type"] == "index":
        to = t[0][1]["position"]
    else:
        to = t[0][1]
    ret = {"type": "span", "from": fr, "to": to}
    if t[0][0].get("fuzzy"):
        ret.setdefault("modifiers", {})
        ret["modifiers"]["from"] = "fuzzy"
    if t[0][1].get("fuzzy"):
        ret.setdefault("modifiers", {})
        ret["modifiers"]["to"] = "fuzzy"
    return ret

def _l_site(t):
    return {
        "type": "site",
        "between": t[0][:]
    }

def _l_choice(t):
    return {
        "type": "choice",
        "between": t[0][:]
    }

def _l_gap(t):
    return {
        "type": "gap",
        "length": t[0][1]
    }

def _l_complement(t):
    return {
        "type": "complement",
        "segment": t[0][1]
    }

def _l_join(t):
    return {
        "type": "join",
        "segments": t[0][1:]
    }

def _l_order(t):
    return {
        "type": "order",
        "segments": t[0][1:]
    }

def _l_referenceloc(t):
    return {
        "type": "reference",
        "accession": t[0][0],
        "segment": t[0][1]
    }

loctypenames = """
    index bond one_of span site choice gap complement join order referenceloc
""".split()

for l in loctypenames:
    locals()[l].setParseAction(locals()["_l_%s" % l])


#
# Qualifier Parsers
#

_qual_default = lambda d: d.strip('"')
_q_allele = _qual_default
_q_bond_type = _qual_default
_q_chromosome = _qual_default
_q_clone = _qual_default
_q_clone_lib = _qual_default
_q_coded_by = _qual_default
_q_codon_start = lambda d: int(d)
_q_country = _qual_default
_q_cultivar = _qual_default
_q_db_xref = _qual_default
_q_dev_stage = _qual_default
_q_ec_number = _qual_default
_q_evidence = _qual_default
_q_gene = _qual_default
_q_go_component = _qual_default
_q_go_function = _qual_default
_q_go_process = _qual_default
_q_isolate = _qual_default
_q_map = _qual_default
_q_mol_type = _qual_default
_q_note = lambda d: " ".join(d.split())
_q_number = lambda d: int(d)
_q_organelle = _qual_default
_q_organism = _qual_default
_q_product = _qual_default
_q_protein_id = _qual_default
_q_pseudo = lambda d: True
_q_region_name = _qual_default
_q_rpt_family = _qual_default
_q_site_type = _qual_default
_q_standard_name = _qual_default
_q_strain = _qual_default
_q_tissue_type = _qual_default
_q_transcript_id = _qual_default
_q_transl_table = _qual_default
_q_translation = lambda d: ''.join(d.split())
_q_virion = lambda d: True

MULTI_QUALIFIERS = set(["allele", "db_xref"])
def _add_qualifier(s, quals, name, data):
    if name not in MULTI_QUALIFIERS:
        if name in quals:
            warnings.warn("Unexpected qualifier repetition: %s" % name)
        else:
            quals[name] = data
            return
    if name not in quals:
        quals[name] = []
    elif name in quals and not isinstance(quals[name], list):
        quals[name] = [quals[name]]
    quals[name].append(data)


#
# Public parsing methods
#

def parse_locus(data):
    return locus.parseString(data).asDict()

def parse_keyword(data):
    name = data.split(None, 1)[0].lower()
    try:
        func = globals()["_k_%s" % name]
        return func(data)
    except KeyError:
        warnings.warn("No keyword parser for: %r" % name)
        return data

def parse_keywords(data):
    ret = {}
    res = keywordsection.parseString(data)
    for kw in res:
        name = kw.split(None, 1)[0].lower()
        kwdata = parse_keyword(kw)
        if name not in MULTI_KEYWORDS:
            if name in ret:
                raise KeyError("Keyword '%s' is not repeatable." % name)
            ret[name] = kwdata
        else:
            if name not in ret:
                ret[name] = []
            ret[name].append(kwdata)
    return ret

def parse_location(data):
    return location.parseString(data)[0]

def parse_feature(data):
    res = featgroup.parseString(data)
    props = {}
    for q in res[2:]:
        qname = q[0].lower()
        value = q[1] if len(q) > 1 else None
        func = globals().get("_q_%s" % qname)
        if func is None:
            warnings.warn("No parser for qualifier: %s" % qname)
            _add_qualifier(data, props, qname, value)
        else:
            _add_qualifier(data, props, qname, func(value))
    return {
        "type": res[0],
        "location": parse_location(res[1]),
        "properties": props
    }

def parse_features(data):
    ret = []
    for feat in featuresection.parseString(data):
        ret.append(parse_feature(feat))
    return ret

def parse_contig(data):
    return contig.parseString(data)[0]

def parse_base_count(data):
    res = base_count.parseString(data)
    return dict((g[1].upper(), g[0]) for g in res)

class Reader(object):
    def __init__(self, stream):
        self.stream = itertools.ifilter(Reader.skipblank, stream)

    def __iter__(self):
        return self

    @staticmethod
    def skipblank(line):
        return bool(line.strip())

    @staticmethod
    def from_string(strdata):
        def _iter(data):
            prev = 0
            next = data.find("\n")
            while next >= 0:
                yield data[prev:next]
                prev, next = next, data.find("\n", next+1)
            yield data[prev:]
        return Reader(_iter(strdata))

    def next(self):
        return self.stream.next()
    
    def read_to(self, marker):
        lines = []
        for line in self.stream:
            if line.startswith(marker):
                return (''.join(lines), line)
            lines.append(line)
        return (''.join(lines), None)

class Record(object):
    def __init__(self, stream):
        if not isinstance(stream, Reader):
            stream = Reader(iter(stream))
        
        self.locus = parse_locus(stream.next())
        self.keywords = parse_keywords(stream.read_to("FEATURES")[0])

        if self.locus["division"] == "CON":
            data = stream.read_to("//")[0]
            pos = data.find("CONTIG")
            self.features = parse_features(data[:pos])
            self.contig = parse_contig(data[pos:])
            self.base_count = None
            self.seqiter = None
        else:
            data, marker = stream.read_to(("ORIGIN", "BASE COUNT"))
            self.features = parse_features(data)
            self.contig = None
            self.base_count = None
            if marker.startswith("BASE COUNT"):
                self.base_count = parse_base_count(marker)
            self.seqiter = Sequence(stream)

    def __repr__(self):
        return "<Record %r>" % self.locus["name"]

    def exhaust(self):
        if not self.seqiter:
            return
        for seq in self.seqiter:
            pass

class Sequence(object):
    def __init__(self, stream):
        self.exhausted = False
        self.stream = stream

    def __iter__(self):
        return self

    def next(self):
        if self.exhausted:
            raise StopIteration
        line = self.stream.next()
        if line.strip() == "//":
            self.exhausted = True
            raise StopIteration
        return ''.join(line.split()[1:])


#
# Main Entry Points
#

def parse(data):
    if isinstance(data, types.StringTypes):
        stream = Reader.from_string(data)
    else:
        stream = Reader(iter(data))
    while True:
        rec = Record(stream)
        yield rec
        rec.exhaust()

def parse_file(filename):
    # Round about way to make sure the file
    # stays open for the lifetime of the record.
    def _stream(fname):
        with open(fname) as handle:
            for line in handle:
                yield line
    for r in parse(_stream(filename)):
        yield r
