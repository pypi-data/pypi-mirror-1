#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import datetime

def test_locus(rec):
    assert rec.locus == {
        "name": "EU140800",
        "length": 3390,
        "base_type": "bp",
        "molecule_type": "mRNA",
        "topology": "linear",
        "division": "PRI",
        "date": datetime.date(2007, 9, 29)
    }

def test_keywords(rec):
    assert rec.keywords == {
        "definition": " ".join("""
            Homo sapiens intersectin 1 short form variant 3 (ITSN1) mRNA,
            complete cds, alternatively spliced
        """.split()),
        "accession": {"primary": "EU140800", "secondary": []},
        "version": {"accession": "EU140800.1", "gi": "157497185"},
        "keywords": [],
        "source": {
            "name": "Homo sapiens (human)",
            "organism": "Homo sapiens",
            "taxonomy": """
                Eukaryota Metazoa Chordata Craniata Vertebrata Euteleostomi
                Mammalia Eutheria Euarchontoglires Primates Haplorrhini
                Catarrhini Hominidae Homo
            """.split()
        },
        "reference": [{
            "refid": 1,
            "location": {"from": 1, "to": 3390},
            "notes": "",
            "authors": "Kropyvko,S., Tsyba,L., Skrypkina,I. and Rynditch,A.",
            "title": " ".join("""
                Isolation and characterization of the novel complete coding
                sequence isoforms of intersectin 1
            """.split()),
            "journal": "Unpublished"
        },{
            "refid": 2,
            "location": {"from": 1, "to": 3390},
            "notes": "",
            "authors": "Kropyvko,S., Tsyba,L., Skrypkina,I. and Rynditch,A.",
            "title": "Direct Submission",
            "journal": " ".join("""
                Submitted (06-SEP-2007) Department of Functional Genomics,
                Institute of Molecular Biology and Genetics, 150 Zabolotnogo Str.,
                Kyiv 03143, Ukraine
            """.split())
        }]
    }

def test_features(rec):
    assert rec.features == [
        {
            "type": "source",
            "location": {"type": "span", "from": 1, "to": 3390},
            "properties": {
                "organism": "Homo sapiens",
                "mol_type": "mRNA",
                "db_xref": ["taxon:9606"],
                "chromosome": "21",
                "map": "21q22.1-q22.2",
                "tissue_type": "brain",
                "dev_stage": "12 week embryo"
            }
        },
        {
            "type": "gene",
            "location": {"type": "span", "from": 1, "to": 3390},
            "properties": {
                "gene": "ITSN1"
            }
        },
        {
            "type": "CDS",
            "location": {"type": "span", "from": 2, "to": 3340},
            "properties": {
                "gene": "ITSN1",
                "note": " ".join("""
                    alternatively spliced; produced by truncation of
                    exon 6 and alternative splicing of exons 25 and 26
                """.split()),
                "codon_start": 1,
                "product": "intersectin 1 short form variant 3",
                "protein_id": "ABV58336.1",
                "db_xref": ["GI:157497186"],
                "translation": "".join("""
                    MAQFPTPFGGSLDIWAITVEERAKHDQQFHSLKPISGFITGDQA
                    RNFFFQSGLPQPVLAQIWALADMNNDGRMDQVEFSIAMKLIKLKLQGYQLPSALPPVM
                    KQQPVAISSAPAFAAVPPLANGAPPVIQPLPAFAHPAATLPKSSSFSRSGPGSQLNTK
                    LQKAQSFDVASVPPVAEWAVPQSSRLKYRQLFNSHDKTMSGHLTGPQARTILMQSSLP
                    QAQLASIWNLSDIDQDGKLTAEEFILAMHLIDVAMSGQPLPPVLPPEYIPPSFRRVRS
                    GSGISVISSTSVDQRLPEEPVLEDEQQQLEKKLPVTFEDKKRENFERGNLELEKRRQA
                    LLEQQRKEQERLAQLERAEQERKERERQEQERKRQLELEKQLEKQRELERQREEERRK
                    EIERREAAKRELERQRQLEWERNRRQELLNQRNKEQEDIVVLKAKKKTLEFELEALND
                    KKHQLEGKLQDIRCRLTTQRQEIESTNKSRELRIAEITHLQQQLQESQQMLGRLIPEK
                    QILNDQLKQVQQNSLHRDSLVTLKRALEAKELARQHLRDQLDEVEKETRSKLQEIDIF
                    NNQLKELREIHNKQQLQKQKSMEAERLKQKEQERKIIELEKQKEEAQRRAQERDKQWL
                    EHVQQEDEHQRPRKLHEEEKLKREESVKKKDGEEKGKQEAQDKLGRLFHQHQEPAKPA
                    VQAPWSTAEKGPLTISAQENVKVVYYRALYPFESRSHDEITIQPGDIVMVKGEWVDES
                    QTGEPGWLGGELKGKTGWFPANYAEKIPENEVPAPVKPVTDSTSAPAPKLALRETPAP
                    LAVTSSEPSTTPNNWADFSSTWPTSTNEKPETDNWDAWAAQPSLTVPSAGQLRQRSAF
                    TPATATGSSPSPVLGQGEKVEGLQAQALYPWRAKKDNHLNFNKNDVITVLEQQDMWWF
                    GEVQGQKGWFPKSYVKLISGPIRKSTSMDSGSSESPASLKRVASPAAKPVVSGEEIAQ
                    VIASYTATGPEQLTLAPGQLILIRKKNPGGWWEGELQARGKKRQIGWFPANYVKLLSP
                    GTSKITPTEPPKSTALAAVCQVIGMYDYTAQNDDELAFNKGQIINVLNKEDPDWWKGE
                    VNGQVGLFPSNYVKLTTDMDPSQQ
                """.split())
            }
        },
        {
            "type": "3'UTR",
            "location": {"type": "span", "from": 3341, "to": 3390},
            "properties": {
                "gene": "ITSN1"
            }
        }
    ]

def test_sequence(rec):
    data = """
        catggctcagtttccaacaccttttggtggcagcctggatatctgggccataactgtaga
        ggaaagagcgaagcatgatcagcagttccatagtttaaagccaatatctggattcattac
        tggtgatcaagctagaaactttttttttcaatctgggttacctcaacctgttttagcaca
        gatatgggcactagctgacatgaataatgatggaagaatggatcaagtggagttttccat
        agctatgaaacttatcaaactgaagctacaaggatatcagctaccctctgcacttccccc
        tgtcatgaaacagcaaccagttgctatttctagcgcaccagcatttgcagctgtgccccc
        cctggctaacggggctccccctgttatacaacctctgcctgcatttgctcatcctgcagc
        cacattgccaaagagttcttcctttagtagatctggtccagggtcacaactaaacactaa
        attacaaaaggcacagtcatttgatgtggccagtgtcccaccagtggcagagtgggctgt
        tcctcagtcatcaagactgaaatacaggcaattattcaatagtcatgacaaaactatgag
        tggacacttaacaggtccccaagcaagaactattcttatgcagtcaagtttaccacaggc
        tcagctggcttcaatatggaatctttctgacattgatcaagatggaaaacttacagcaga
        ggaatttatcctggcaatgcacctcattgatgtagctatgtctggccaaccactgccacc
        tgtcctgcctccagaatacattccaccttcttttagaagagttcgatctggcagtggtat
        atctgtcataagctcaacatctgtagatcagaggctaccagaggaaccagttttagaaga
        tgaacaacaacaattagaaaagaaattacctgtaacgtttgaagataagaagcgggagaa
        ctttgaacgtggcaacctggaactggagaaacgaaggcaagctctcctggaacagcagcg
        caaggagcaggagcgcctggcccagctggagcgggcggagcaggagaggaaggagcgtga
        gcgccaggagcaagagcgcaaaagacaactggaactggagaagcaactggaaaagcagcg
        ggagctagaacggcagagagaggaggagaggaggaaagaaattgagaggcgagaggctgc
        aaaacgggaacttgaaaggcaacgacaacttgagtgggaacggaatcgaaggcaagaact
        actaaatcaaagaaacaaagaacaagaggacatagttgtactgaaagcaaagaaaaagac
        tttggaatttgaattagaagctctaaatgataaaaagcatcaactagaagggaaacttca
        agatatcagatgtcgattgaccacccaaaggcaagaaattgagagcacaaacaaatctag
        agagttgagaattgccgaaatcacccatctacagcaacaattacaggaatctcagcaaat
        gcttggaagacttattccagaaaaacagatactcaatgaccaattaaaacaagttcagca
        gaacagtttgcacagagattcacttgttacacttaaaagagccttagaagcaaaagaact
        agctcggcagcacctacgagaccaactggatgaagtggagaaagaaactagatcaaaact
        acaggagattgatattttcaataatcagctgaaggaactaagagaaatacacaataagca
        acaactccagaagcaaaagtccatggaggctgaacgactgaaacagaaagaacaagaacg
        aaagatcatagaattagaaaaacaaaaagaagaagcccaaagacgagctcaggaaaggga
        caagcagtggctggagcatgtgcagcaggaggacgagcatcagagaccaagaaaactcca
        cgaagaggaaaaactgaaaagggaggagagtgtcaaaaagaaggatggcgaggaaaaagg
        caaacaggaagcacaagacaagctgggtcggcttttccatcaacaccaagaaccagctaa
        gccagctgtccaggcaccctggtccactgcagaaaaaggtccacttaccatttctgcaca
        ggaaaatgtaaaagtggtgtattaccgggcactgtacccctttgaatccagaagccatga
        tgaaatcactatccagccaggagacatagtcatggttaaaggggaatgggtggatgaaag
        ccaaactggagaacccggctggcttggaggagaattaaaaggaaagacagggtggttccc
        tgcaaactatgcagagaaaatcccagaaaatgaggttcccgctccagtgaaaccagtgac
        tgattcaacatctgcccctgcccccaaactggccttgcgtgagacccccgcccctttggc
        agtaacctcttcagagccctccacgacccctaataactgggccgacttcagctccacgtg
        gcccaccagcacgaatgagaaaccagaaacggataactgggatgcatgggcagcccagcc
        ctctctcaccgttccaagtgccggccagttaaggcagaggtccgcctttactccagccac
        ggccactggctcctccccgtctcctgtgctaggccagggtgaaaaggtggaggggctaca
        agctcaagccctatatccttggagagccaaaaaagacaaccacttaaattttaacaaaaa
        tgatgtcatcaccgtcctggaacagcaagacatgtggtggtttggagaagttcaaggtca
        gaagggttggttccccaagtcttacgtgaaactcatttcagggcccataaggaagtctac
        aagcatggattctggttcttcagagagtcctgctagtctaaagcgagtagcctctccagc
        agccaagccggtcgtttcgggagaagaaattgcccaggttattgcctcatacaccgccac
        cggccccgagcagctcactctcgcccctggtcagctgattttgatccgaaaaaagaaccc
        aggtggatggtgggaaggagagctgcaagcacgtgggaaaaagcgccagataggctggtt
        cccagctaattatgtaaagcttctaagccctgggacgagcaaaatcactccaacagagcc
        acctaagtcaacagcattagcggcagtgtgccaggtgattgggatgtacgactacaccgc
        gcagaatgacgatgagctggccttcaacaagggccagatcatcaacgtcctcaacaagga
        ggaccctgactggtggaaaggagaagtcaatggacaagtggggctcttcccatccaatta
        tgtgaagctgaccacagacatggacccaagccagcaatgaatcatatgttgtccatcccc
        ccctcaggcttgaaagtcctcaaagagacc
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
