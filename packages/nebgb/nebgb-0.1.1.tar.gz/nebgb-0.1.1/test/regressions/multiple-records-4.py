#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import datetime

def test_name(rec):
    assert rec.locus["name"] == "BRRBIF72"
    assert rec.locus["date"] == datetime.date(1996, 3, 1)

def test_keyword(rec):
    assert rec.keywords["keywords"] == []

def test_feature(rec):
    assert rec.features[0]["properties"]["dev_stage"] == "flower" #power

def test_counts(rec):
    assert rec.base_count == {"A": 88, "C": 56, "G": 80, "T": 58}

def test_sequence(rec):
    data = """
        aacaaaactc aataaataaa caaatggcag acaacaagca gagcttccaa gccggtcaag
        ccgctggtcg tgctgaggag aagggtaatg tgctgctgat ggacaaggtc aaggatgctg
        ctaccgcagc tggagctctc caaaccgcgg gacagaagat aacggaggcg gcagggggag
        ccgttaatct cgtgaaggag aagaccggca tgaacaagta gccccattgg aaacaaaatt
        gggagttata gtttcctttt taatattaat cgttgtggtt tt
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
