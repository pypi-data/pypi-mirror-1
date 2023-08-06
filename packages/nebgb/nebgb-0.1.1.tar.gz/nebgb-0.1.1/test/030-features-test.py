#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_feature")
def test_basic():
    """
    source          1..182
                    /organism="Mus musculus"
                    /db_xref="taxon:10090"
                    /chromosome="4"
                    /map="4 42.6 cM"
    """
    return {
        "type": "source",
        "location": {"type": "span", "from": 1, "to": 182},
        "properties": {
            "organism": "Mus musculus",
            "db_xref": ["taxon:10090"],
            "chromosome": "4",
            "map": "4 42.6 cM"
        }
    }
    
@t.parse("parse_feature")
def test_multiline_qualifiers():
    """
    CDS             2..3340
                    /gene="ITSN1"
                    /note="alternatively spliced; produced by truncation of
                    exon 6 and alternative splicing of exons 25 and 26"
                    /db_xref="GI:157497186"
                    /translation="MAQFPTPFGGSLDIWAITVEERAKHDQQFHSLKPISGFITGDQA
                    VNGQVGLFPSNYVKLTTDMDPSQQ"
    """
    return {
        "type": "CDS",
        "location": {"type": "span", "from": 2, "to": 3340},
        "properties": {
            "gene": "ITSN1",
            "note": t.normalize("""
                alternatively spliced; produced by truncation of
                exon 6 and alternative splicing of exons 25 and 26
            """),
            "db_xref": ["GI:157497186"],
            "translation": "".join("""
                MAQFPTPFGGSLDIWAITVEERAKHDQQFHSLKPISGFITGDQA
                VNGQVGLFPSNYVKLTTDMDPSQQ        
            """.split())
        }
    }
    
@t.parse("parse_feature")
def test_multiline_location():
    """
    CDS             complement(join(70720..70988,71424..71621,72605..72768,
                    72839..73016,73086..73559,75217..75241))
                    /gene="EG:BACR25B3.2"
    """
    return {
        "type": "CDS",
        "location": {
            "type": "complement",
            "segment": {
                "type": "join",
                "segments": [
                    {"type": "span", "from": 70720, "to": 70988},
                    {"type": "span", "from": 71424, "to": 71621},
                    {"type": "span", "from": 72605, "to": 72768},
                    {"type": "span", "from": 72839, "to": 73016},
                    {"type": "span", "from": 73086, "to": 73559},
                    {"type": "span", "from": 75217, "to": 75241}
                ]
            }
        },
        "properties": {
            "gene": "EG:BACR25B3.2",
        }
    }

@t.parse("parse_feature")
def test_qualifier_no_value():
    """
    CDS             1..360
                    /pseudo
                    /gene="CNR2"
    """
    return {
        "type": "CDS",
        "location": {"type": "span", "from": 1, "to": 360},
        "properties": {
            "pseudo": True,
            "gene": "CNR2"
        }
    }

@t.parse("parse_feature")
def test_qualifier_fake_out():
    """
    source          1..1326
                    /organism="Homo sapiens"
                    /db_xref="taxon:9606"
                    /chromosome="21"
                    /clone="IMAGE cDNA clone 125195"
                    /clone_lib="Soares fetal liver spleen 1NFLS"
                    /note="contains Alu repeat; likely to be be derived from
                    unprocessed nuclear RNA or genomic DNA; encodes putative
                    exons identical to FTCD; formimino transferase
                    cyclodeaminase; formimino transferase (EC 2.1.2.5)
                    /formimino tetrahydro folate cyclodeaminase (EC 4.3.1.4)"
    """
    return {
        "type": "source",
        "location": {"type": "span", "from": 1, "to": 1326},
        "properties": {
            "organism": "Homo sapiens",
            "db_xref": ["taxon:9606"],
            "chromosome": "21",
            "clone": "IMAGE cDNA clone 125195",
            "clone_lib": "Soares fetal liver spleen 1NFLS",
            "note": t.normalize("""
                contains Alu repeat; likely to be be derived from
                unprocessed nuclear RNA or genomic DNA; encodes putative
                exons identical to FTCD; formimino transferase
                cyclodeaminase; formimino transferase (EC 2.1.2.5)
                /formimino tetrahydro folate cyclodeaminase (EC 4.3.1.4)
            """)
        }    
    }

@t.parse("parse_feature")
def test_weird_qualifier_name():
    """
    3'UTR           3341..3390
                    /gene="ITSN1"
    """
    return {
        "type": "3'UTR",
        "location": {"type": "span", "from": 3341, "to": 3390},
        "properties": {
            "gene": "ITSN1"
        }
    }

@t.parse("parse_feature")
def test_no_qualifiers():
    """
    sig_peptide     1..21
    """
    return {
        "type": "sig_peptide",
        "location": {"type": "span", "from": 1, "to": 21},
        "properties": {}
    }

@t.parse("parse_feature")
def test_transl_except():
    """
    CDS             3205759..3205994
                    /gene="CROCCL2"
                    /codon_start=1
                    /transl_except=(pos:complement(3205818..3205820),aa:OTHER)
    """
    return {
        "type": "CDS",
        "location": {"type": "span", "from": 3205759, "to": 3205994},
        "properties": {
            "gene": "CROCCL2",
            "codon_start": 1,
            "transl_except": [{
                "acid": "OTHER",
                "location": {
                    "type": "complement",
                    "segment": {
                        "type": "span",
                        "from": 3205818,
                        "to": 3205820,
                    }
                }
            }]
        }
    }