#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "BNAKINI"

def test_keyword(rec):
    assert rec.keywords["reference"][0]["refid"] == 1

def test_feature(rec):
    assert rec.features[5]["properties"]["gene"] == "kin1"

def test_counts(rec):
    assert rec.base_count == {"A": 129, "C": 76, "G": 110, "T": 126}

def test_sequence(rec):
    data = """
        aaaaaaacac aacaaaactc aataaataaa caaatggcag acaacaagca gagcttccaa
        gccggtcaag cctctggtcg tgctgaggag aagggtaatg tgctgatgga caaggtcaag
        gatgctgcta ccgcagctgg agcgtctgcg caaaccgcgg gacagaagat aacggaggcg
        gcagggggag ccgttaatct cgtgaaggag aagaccggca tgaacaagta gccccattgg
        aaataaaatt gggagttata gtttcccttt ttaatgttaa tcgttgtggt tttaaataaa
        aattgggtgt tctaattgat cttcaccgta gttgttgttg ttgttgtttt tagtgtttga
        agtaatgttt tcaaccttta ggtgtatgtc ttgatgttta tgtacttagt tcccccttaa
        tgaacatctg atttaagctt c
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())