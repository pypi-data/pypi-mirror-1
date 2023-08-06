#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "DMBR25B3"

def test_kw_length(rec):
    assert len(rec.keywords) == 7
    assert len(rec.keywords["reference"]) == 2

def test_feature_length(rec):
    assert len(rec.features) == 25
    
def test_feature_prop_lengths(rec):
    data = [
        3,
        1, 6, 1, 6, 1, 6, 1, 6, 1, 6, 1, 6,
        1, 6, 1, 6, 1, 6, 1, 5, 1, 6, 1, 5
    ]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_first_bad_qual(rec):
    data = ' '.join("""
         /prediction=(method:''genefinder'',
         version:''084'', score:''105.71'');
         /prediction=(method:''genscan'', version:''1.0'');
         /match=(desc:''BASEMENT MEMBRANE-SPECIFIC HEPARAN SULFATE
         PROTEOGLYCAN CORE PROTEIN PRECURSOR (HSPG) (PERLECAN)
         (PLC)'', species:''Homo sapiens (Human)'',
         ranges:(query:24292..24549,
         target:SWISS-PROT::P98160:3713..3628, score:''201.00''),
         (query:24016..24291, target:SWISS-PROT::P98160:3815..3724,
         score:''139.00''), (query:23857..24006,
         target:SWISS-PROT::P98160:3866..3817, score:''99.00''),
         (query:24052..24327, target:SWISS-PROT::P98160:4059..3968,
         score:''143.00''), (query:24046..24312,
         target:SWISS-PROT::P98160:4341..4253, score:''116.00''),
         (query:23806..23901, target:SWISS-PROT::P98160:4177..4146,
         score:''76.00''), (query:23203..23382,
         target:SWISS-PROT::P98160:4062..4003, score:''116.00''),
         (query:22523..22777, target:SWISS-PROT::P98160:4288..4204,
         score:''112.00''), (query:22235..22300,
         target:SWISS-PROT::P98160:4358..4337, score:''64.00'')),
         method:''blastx'', version:''1.4.9'');
         /match=(desc:''GM03359.5prime GM Drosophila melanogaster
         ovary BlueScript Drosophila melanogaster cDNA clone
         GM03359 5prime, mRNA sequence'', species:''Drosophila
         melanogaster (fruit fly)'', ranges:(query:25024..25235,
         target:EMBL::AA801707:438..227, score:''1024.00''),
         (query:24851..24898, target:EMBL::AA801707:476..429,
         score:''204.00'')), method:''blastn'', version:''1.4.9'');
         /match=(desc:''LD08615.5prime LD Drosophila melanogaster
         embryo BlueScript Drosophila melanogaster cDNA clone
         LD08615 5prime, mRNA sequence'', species:''Drosophila
         melanogaster (fruit fly)'', ranges:(query:24629..24727,
         target:EMBL::AA264808:99..1, score:''495.00''),
         (query:24417..24566, target:EMBL::AA264808:250..101,
         score:''687.00''), (query:24048..24420,
         target:EMBL::AA264808:618..246, score:''1847.00''),
         (query:23986..24036, target:EMBL::AA264808:678..628,
         score:''237.00'')), method:''blastn'', version:''1.4.9'');
         /match=(desc:''HL02745.5prime HL Drosophila melanogaster
         head BlueScript Drosophila melanogaster cDNA clone HL02745
         5prime, mRNA sequence'', species:''Drosophila melanogaster
         (fruit fly)'', ranges:(query:23944..24045,
         target:EMBL::AA697546:103..2, score:''510.00''),
         (query:23630..23943, target:EMBL::AA697546:416..103,
         score:''1570.00''), (query:23419..23561,
         target:EMBL::AA697546:558..416, score:''715.00''),
         (query:23306..23417, target:EMBL::AA697546:670..559,
         score:''524.00''), (query:23280..23316,
         target:EMBL::AA697546:695..659, score:''167.00'')),
         method:''blastn'', version:''1.4.9'');
         /match=(desc:''GM08137.5prime GM Drosophila melanogaster
         ovary BlueScript Drosophila melanogaster cDNA clone
         GM08137 5prime, mRNA sequence'', species:''Drosophila
         melanogaster (fruit fly)'', ranges:(query:23235..23278,
         target:EMBL::AA696682:44..1, score:''139.00''),
         (query:22986..23251, target:EMBL::AA696682:294..29,
         score:''1321.00'')), method:''blastn'',
         version:''1.4.9'')
    """.split())
    assert data == rec.features[2]["properties"]["note"]

def test_base_counts(rec):
    assert rec.base_count == {"A": 42902, "C": 33790, "G": 34046, "T": 43591}