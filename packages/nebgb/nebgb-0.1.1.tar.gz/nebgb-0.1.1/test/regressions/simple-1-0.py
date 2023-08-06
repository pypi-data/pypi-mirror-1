#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import datetime
import textwrap

def test_locus(rec):
    assert rec.locus == {
        "name": "NP_034640",
        "length": 182,
        "base_type": "aa",
        "division": "ROD",
        "date": datetime.date(2000, 11, 1)
    }

def test_keywords(rec):
    assert rec.keywords == {
        "definition": "interferon beta, fibroblast [Mus musculus]",
        "accession": {"primary": "NP_034640", "secondary": []},
        "pid": "g6754304",
        "version": {"accession": "NP_034640.1", "gi": "6754304"},
        "dbsource": "REFSEQ: accession NM_010510.1",
        "keywords": [],
        "source": {
            "name": "house mouse",
            "organism": "Mus musculus",
            "taxonomy": """
                Eukaryota Metazoa Chordata Craniata Vertebrata Euteleostomi
                Mammalia Eutheria Rodentia Sciurognathi Muridae Murinae Mus
            """.split()
        },
        "reference": [{
            "refid": 1,
            "location": {"from": 1, "to": 182},
            "notes": "",
            "authors": " ".join("""
                Higashi,Y., Sokawa,Y., Watanabe,Y., Kawade,Y., Ohno,S.,
                Takaoka,C. and Taniguchi,T.
            """.split()),
            "title": "structure and expression of a cloned cdna for mouse interferon-beta",
            "journal": "J. Biol. Chem. 258, 9522-9529 (1983)",
            "medline": "83265757",
        }],
        "comment": textwrap.dedent("""
            PROVISIONAL REFSEQ: This record has not yet been subject to final
            NCBI review. The reference sequence was derived from K00020.1.
        """.lstrip("\n").rstrip())
    }

def test_features(rec):
    assert rec.features == [
        {
            "type": "source",
            "location": {"type": "span", "from": 1, "to": 182},
            "properties": {
                "organism": "Mus musculus",
                "db_xref": ["taxon:10090"],
                "chromosome": "4",
                "map": "4 42.6 cM"
            }
        },
        {
            "type": "Protein",
            "location": {"type": "span", "from": 1, "to": 182},
            "properties": {
                "product": "interferon beta, fibroblast"
            }
        },
        {
            "type": "sig_peptide",
            "location": {"type": "span", "from": 1, "to": 21},
            "properties": {}
        },
        {
            "type": "Region",
            "location": {"type": "span", "from": 1, "to": 182},
            "properties": {
                "region_name": "Interferon alpha/beta domain",
                "db_xref": ["CDD:pfam00143"],
                "note": "interferon"
            }
        },
        {
            "type": "mat_peptide",
            "location": {"type": "span", "from": 22, "to": 182},
            "properties": {
                "product": "ifn-beta"
            }
        },
        {
            "type": "Region",
            "location": {"type": "span", "from": 56, "to": 170},
            "properties": {
                "region_name": "Interferon alpha, beta and delta.",
                "db_xref": ["CDD:IFabd"],
                "note": "IFabd"
            }
        },
        {
            "type": "CDS",
            "location": {"type": "span", "from": 1, "to": 182},
            "properties": {
                "gene": "Ifnb",
                "db_xref": ["LocusID:15977", "MGD:MGI:107657"],
                "coded_by": "NM_010510.1:21..569"
            }
        }
    ]

def test_sequence(rec):
    data = """
        mnnrwilhaa fllcfsttal sinykqlqlq ertnirkcqe lleqlngkin ltyradfkip
        memtekmqks ytafaiqeml qnvflvfrnn fsstgwneti vvrlldelhq qtvflktvle
        ekqeerltwe msstalhlks yywrvqrylk lmkynsyawm vvraeifrnf liirrltrnf
        qn
    """
    assert ''.join(s for s in rec.seqiter) == ''.join(data.split())
