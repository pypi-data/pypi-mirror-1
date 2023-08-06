#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "ATKIN2"

def test_keyword(rec):
    assert rec.keywords["source"]["name"] == "thale cress"

def test_feature(rec):
    assert rec.features[2]["properties"]["number"] == 1

def test_counts(rec):
    assert rec.base_count == {"A": 263, "C": 155, "G": 160, "T": 302}

def test_sequence(rec):
    data = """
        atttggccta taaatataaa cccttaagcc cacatatctt ctcaatccat cacaaacaaa
        acacacatca aaaacgattt tacaagaaaa aaatatctga aaaatgtcag agaccaacaa
        gaatgccttc caagccggtc aggccgctgg caaagctgag gtactctttc tctcttagaa
        cagagtactg atagattgtt caagttataa ctctttgaaa acagttgaaa cttgatcact
        cctagaactt ccattttctt gtttaattta gtttgtcgta attatgtaat tgattttgtg
        ttgaccatgg ttgttatata ggagaagagc aatgttctgc tggacaaggc caaggatgct
        gctgctgcag ctggagcttc cgcgcaacag gtaaacgatc tatacacaca ttatgacatt
        tatgtaaaga atgaaaagtc ttcttagagc atacatttac gcagatttct gatattttca
        tatggtttga tgtaaatgtt ataggcggga aagagtatat cggatgcggc agtgggaggt
        gttaacttcg tgaaggacaa gaccggcctg aacaagtagc gatccgagtc aactttggga
        gttataattt cccttttcta attaattgtt gggattttca aataaaattt gggagtcata
        attgattctc gtactcatcg tacttgttgt tgtttttagt gttgtaatgt tttaatgttt
        cttctccctt tagatgtact acgtttggaa ctttaagttt aatcaacaaa atctagttta
        agttctaaga actttgtttt accatcctct tttttattgc acttaatgct tatagacttt
        tatctccatc catttctcaa ttcggctacg ttgaattata
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())