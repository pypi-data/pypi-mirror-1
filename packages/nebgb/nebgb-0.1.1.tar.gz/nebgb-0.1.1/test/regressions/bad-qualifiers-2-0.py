#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "IRO125195"

def test_kw_length(rec):
    assert len(rec.keywords) == 7
    assert len(rec.keywords["reference"]) == 2

def test_feature_length(rec):
    assert len(rec.features) == 5
    
def test_feature_prop_lengths(rec):
    data = [6, 1, 2, 2, 2]
    for r, e in zip(rec.features, data):
        assert len(r["properties"]) == e

def test_first_bad_qual(rec):
    data = ' '.join("""
          contains Alu repeat; likely to be be derived from
          unprocessed nuclear RNA or genomic DNA; encodes putative
          exons identical to FTCD; formimino transferase
          cyclodeaminase; formimino transferase (EC 2.1.2.5)
          /formimino tetrahydro folate cyclodeaminase (EC 4.3.1.4)
    """.split())
    assert data == rec.features[0]["properties"]["note"]

def test_sequence(rec):
    data = "".join("""
        cacaggccca gagccactcc tgcctacagg ttctgagggc tcaggggacc tcctgggccc
        tcaggctctt tagctgagaa taagggccct gagggaacta cctgcttctc acatccccgg
        gtctctgacc atctgctgtg tgccccgacc ccccctaccc tgctcctcca ccaagcctga
        tgccaagggc tataaaccac tggcccaaca gaagcttggt tcccagagaa ctggtccctg
        cctgggacat gctccttgct acagcccctt gtgggagctc agagggcatg gctgctcccc
        ctacggtccc tcgcccagtg gttctgtctc tttatggcag gaagcaatga ggctccccaa
        gaacacacct gaggaaaagg acaggtgagc ctggagggcc ggccgcaccg tgggcctctg
        tgtctgggga gttggtggcc aggatcccga gtacctgggt gctgtgacgg ggcgtggttg
        gcctgggcgt gctgggtgtt tgggaatgac ttcccatcgc ccgcttctgc agcctgctca
        gccctgttgg ggtgcagtgt gtccactgcc tgcctgtgtg tgccgctgtg ctcaggctct
        cctcttgctc ctttcaggcg cacggcggcc ctacaggagg gtctgaggcg ggcagtctct
        gtgccgctga cgctggcgga gacggtggcc tcgctgtggc cggccctgca ggaactggcc
        cggtgtggga acctggcctg ccggtcagac ctccaggtag gggggcccgg gggaccccag
        gcctcctgcc gcaaagcagg aagcagctgt tggggctgag ttgctggaga gcacggtggt
        tggctgggct gagccaggta gggagacctc acttcacggg cagttcccgg ggctttggcc
        tcctccaaca gggccggggt gtccgctgcc ttctaagatc tcgctcacgg cggcaccaca
        gacggagacc caaatgtgtc tgcagagccc accctgacca ctgtataagt gtatactccc
        ccaagacccc ttgtatcacc cccactgtcg tgttctagaa aacacctatg tcagcccagg
        cacaatggtt ctcgcctgtg gtcccagcac tttgggaggc tgaggcggga ggatcacttg
        aatagaggag gtcgagacca gcctgggcaa catagtggga ccctggctgt acaatagata
        catatgagcc aggcacggtg gtgcctgtgg tcccagctcc ctgcccagcc agcctcctgt
        ctccagagaa gttctccatt aaaaaataat ttagcaaaaa aaaaaaaaaa aaaaaaaaaa
        aaaaaa
    """.split())
    seq = ''.join([s for s in rec.seqiter])
    assert seq == data