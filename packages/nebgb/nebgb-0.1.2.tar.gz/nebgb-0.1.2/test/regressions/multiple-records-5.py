#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "AF297471"

def test_keyword(rec):
    assert rec.keywords["accession"] == {"primary": "AF297471", "secondary": []}

def test_feature(rec):
    assert rec.features[0]["properties"]["cultivar"] == "Cascade"

def test_counts(rec):
    assert rec.base_count == {"A": 155, "C": 89, "G": 116, "T": 137}

def test_sequence(rec):
    data = """
        atggcagaca acaagcagag cttccaagcc ggtcaagccg ctggtcgtgc tgaggtctct
        ttctctcttt aactctctga tcaaatgcag ttgctgcggt taaacaatca cactttataa
        aataaagaga agttatttat attttcttga accaagtaaa tgaatgtatt ttgaccaaaa
        aaagaagaag taaatgaatg tattaattga tttcgtgtgg acaatggtgt gtaaatatag
        gagaagggta atgtgctgat ggacaaggtc aaggatgctg ctaccgcagc tggagcgtct
        gcgcaaaccg taagcgatct accccatgat atataaataa acatacgtct ctactctcta
        ctgtacatgt tcgtagatct catatctttt tatgctgttc taacatgtat ttacgtttat
        aggcgggaca gaagataacg gaggcggcag ggggagccgt taatctcgtg aaggagaaga
        ccggcatgaa caagtag
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
