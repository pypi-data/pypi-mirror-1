#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "ARU237582"

def test_keyword(rec):
    assert rec.keywords["version"] == {
        "accession": "AJ237582.1",
        "gi": "4538892"
    }

def test_feature(rec):
    assert rec.features[4]["type"] == "CDS"
    assert rec.features[4]["properties"]["codon_start"] == 2

def test_counts(rec):
    assert rec.base_count == {"A": 65, "C": 38, "G": 53, "T": 48, "OTHERS": 2}

def test_sequence(rec):
    data = """
        ggacaaggcc aaggatgctg ctgctgcagc tggagcttcc gcgcaacaag taaacagata
        cacacacatg acacatatat aantacatat cacaagtagg tcgtagattt ctgatatntt
        tgtattgtgt attacgtata taggcgggaa agaacatatc ggatgcagca gctggaggtg
        ttaacttcgt gaaggagaag accggc
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
