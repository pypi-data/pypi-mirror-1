#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

def test_name(rec):
    assert rec.locus["name"] == "ATCOR66M"

def test_keyword(rec):
    assert rec.keywords["reference"][1]["medline"] == "92119220"

def test_feature(rec):
    assert rec.features[2]["properties"]["translation"] == "".join("""
        MSETNKNAFQAGQAAGKAEEKSNVLLDKAKDAAAAAGASAQQAG
        KSISDAAVGGVNFVKDKTGLNK
    """.split())

def test_counts(rec):
    assert rec.base_count == {"A": 194, "C": 82, "G": 104, "T": 133}

def test_sequence(rec):
    data = """
        aacaaaacac acatcaaaaa cgattttaca agaaaaaaat atctgaaaaa tgtcagagac
        caacaagaat gccttccaag ccggtcaggc cgctggcaaa gctgaggaga agagcaatgt
        tctgctggac aaggccaagg atgctgctgc tgcagctgga gcttccgcgc aacaggcggg
        aaagagtata tcggatgcgg cagtgggagg tgttaacttc gtgaaggaca agaccggcct
        gaacaagtag cgatccgagt caactttggg agttataatt tcccttttct aattaattgt
        tgggattttc aaataaaatt tgggagtcat aattgattct cgtactcatc gtacttgttg
        ttgtttttag tgttgtaatg ttttaatgtt tcttctccct ttagatgtac tacgtttgga
        actttaagtt taatcaacaa aatctagttt aagttctaaa aaaaaaaaaa aaaaaaaaaa
        aaaaaaaaaa aaaaaaaaaa aaaaaaaaaa aaa
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
