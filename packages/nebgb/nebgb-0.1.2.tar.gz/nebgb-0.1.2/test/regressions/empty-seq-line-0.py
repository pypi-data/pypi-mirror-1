#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "NP_001832"
    assert rec.locus["length"] == 360
    assert rec.locus["base_type"] == "aa"

def test_kw_length(rec):
    assert len(rec.keywords) == 9
    assert len(rec.keywords["reference"]) == 3
    assert len(rec.keywords["source"]["taxonomy"]) == 12

def test_feature_length(rec):
    assert len(rec.features) == 4
    
def test_feature_prop_lengths(rec):
    data = [4, 1, 3, 4]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_pseudo(rec):
    assert rec.features[3] == {
        "type": "CDS",
        "location": {"type": "span", "from": 1, "to": 360},
        "properties": {
            "pseudo": True,
            "gene": "CNR2",
            "db_xref": ["LocusID:1269", "MIM:605051"],
            "coded_by": "NM_001841.1:127..1209"
        }
    }

def test_sequence(rec):
    data = "".join("""
        meecwvteia ngskdgldsn pmkdymilsg pqktavavlc tllgllsale nvavlylils
        shqlrrkpsy lfigslagad flasvvfacs fvnfhvfhgv dskavfllki gsvtmtftas
        vgsllltaid rylclrypps ykalltrgra lvtlgimwvl salvsylplm gwtccprpcs
        elfplipndy llswllfiaf lfsgiiytyg hvlwkahqhv aslsghqdrq vpgmarmrld
        vrlaktlglv lavllicwfp vlalmahsla ttlsdqvkka fafcsmlcli nsmvnpviya
        lrsgeirssa hhclahwkkc vrglgseake eaprssvtet eadgkitpwp dsrdldlsdc
    """.split())
    seq = ''.join([s for s in rec.seqiter])
    assert seq == data
