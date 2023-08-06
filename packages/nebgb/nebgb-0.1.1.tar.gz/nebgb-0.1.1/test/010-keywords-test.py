#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_keyword")
def test_definition():
    """
DEFINITION  Pseudomonas syringae pv. averrhoi strain HL1 leucyl-tRNA synthetase
            (leuS) gene, partial cds; putative lipoprotein, DNA polymerase III
            delta subunit (holA), type III effector HopAJ2 (hopAJ2), lipoic
            acid synthetase (lipA), and lipoate-protein ligase B (lipB) genes,
            complete cds; and hypothetical protein gene, partial cds.
    """
    return t.normalize("""
        Pseudomonas syringae pv. averrhoi strain HL1 leucyl-tRNA synthetase
        (leuS) gene, partial cds; putative lipoprotein, DNA polymerase III
        delta subunit (holA), type III effector HopAJ2 (hopAJ2), lipoic
        acid synthetase (lipA), and lipoate-protein ligase B (lipB) genes,
        complete cds; and hypothetical protein gene, partial cds
    """)
    
@t.parse("parse_keyword")
def test_accession_1():
    "ACCESSION   AL109817"
    return {"primary": "AL109817", "secondary": []}

@t.parse("parse_keyword")
def test_accession_2():
    "ACCESSION   AL109817   NC01231-NC01250"
    return {
        "primary": "AL109817",
        "secondary": [{"first": "NC01231", "last": "NC01250"}]
    }
    
@t.parse("parse_keyword")
def test_accession_3():
    "ACCESSION AL109817 NC01231-NC01250 AL109818"
    return {
        "primary": "AL109817",
        "secondary": [
            {"first": "NC01231", "last": "NC01250"},
            "AL109818"
        ]
    }

@t.parse("parse_keyword")
def test_version():
    "VERSION NC_0012312.4 GI:23923234"
    return {"accession": "NC_0012312.4", "gi": "23923234"}

@t.parse("parse_keyword")
def test_pid():
    "PID         g134354"
    return "g134354"

@t.parse("parse_keyword")
def test_dbsource():
    """
    DBSOURCE    swissprot: locus SCX3_BUTOC, accession P01485;
                class: standard.
                created: Jul 21, 1986.
                sequence updated: Jul 21, 1986.
                annotation updated: Oct 16, 2001.
                xrefs: gi: gi: 69530
    """
    return t.dedent("""
        swissprot: locus SCX3_BUTOC, accession P01485;
        class: standard.
        created: Jul 21, 1986.
        sequence updated: Jul 21, 1986.
        annotation updated: Oct 16, 2001.
        xrefs: gi: gi: 69530
    """, left="\n", right=None)

@t.parse("parse_keyword")
def test_segment():
    "SEGMENT     2 of 6"
    return {"position": 2, "of": 6}
    
@t.parse("parse_keyword")
def test_keywords_1():
    "KEYWORDS    ."
    return []

@t.parse("parse_keyword")
def test_keywords_2():
    "KEYWORDS    FLI_CDNA."
    return ["FLI_CDNA"]

@t.parse("parse_keyword")
def test_keywords_3():
    "KEYWORDS    Neurotoxin; Sodium channel inhibitor; Amidation."
    return ["Neurotoxin", "Sodium channel inhibitor", "Amidation"]

@t.parse("parse_keyword")
def test_keywords_4():
    """
KEYWORDS    antifreeze protein homology; cold-regulated gene; cor6.6 gene; KIN1
            homology.
    """
    return [
        "antifreeze protein homology",
        "cold-regulated gene",
        "cor6.6 gene",
        "KIN1 homology"
    ]

@t.parse("parse_keyword")
def test_source():
    """
    SOURCE      Human immunodeficiency virus 1 (HIV-1)
      ORGANISM  Human immunodeficiency virus 1
                Viruses; Retro-transcribing viruses; Retroviridae;
                Orthoretrovirinae; Lentivirus; Primate lentivirus group.
    """
    return {
        "name": "Human immunodeficiency virus 1 (HIV-1)",
        "organism": "Human immunodeficiency virus 1",
        "taxonomy": [
            "Viruses",
            "Retro-transcribing viruses",
            "Retroviridae",
            "Orthoretrovirinae",
            "Lentivirus",
            "Primate lentivirus group"
        ]
    }

@t.parse("parse_keyword")
def test_reference_1():
    """
REFERENCE   2  (bases 1 to 1005)
  AUTHORS   Paraschiv,S., Tinischi,M., Neaga,E., Costache,M., DInu,M.,
            Florea,M. and Otelea,D.
  TITLE     Direct Submission
  JOURNAL   Submitted (13-JUL-2007) Molecular Diagnostics Laboratory, Institute
            for Infectious Diseases 'Prof. Dr. Matei Bals', Grozovici Street,
            No. 1, Sector 2, Bucharest 021105, Romania
    """
    return {
        "refid": 2,
        "location": {"from": 1, "to": 1005},
        "notes": "",
        "authors": t.normalize("""
            Paraschiv,S., Tinischi,M., Neaga,E., Costache,M., DInu,M.,
            Florea,M. and Otelea,D.
        """),
        "title": "Direct Submission",
        "journal": t.normalize("""
            Submitted (13-JUL-2007) Molecular Diagnostics Laboratory, Institute
            for Infectious Diseases 'Prof. Dr. Matei Bals', Grozovici Street,
            No. 1, Sector 2, Bucharest 021105, Romania
        """)
    }
    
@t.parse("parse_keyword")
def test_reference_2():
    """
REFERENCE   1  (sites)
  AUTHORS   Kaneko,T., Nakamura,Y., Sato,S., Asamizu,E., Kato,T., Sasamoto,S.,
            Watanabe,A., Idesawa,K., Ishikawa,A., Kawashima,K., Kimura,T.,
            Kishida,Y., Kiyokawa,C., Kohara,M., Matsumoto,M., Matsuno,A.,
            Mochizuki,Y., Nakayama,S., Nakazaki,N., Shimpo,S., Sugimoto,M.,
            Takeuchi,C., Yamada,M. and Tabata,S.
  TITLE     Complete genome structure of the nitrogen-fixing symbiotic
            bacterium Mesorhizobium loti
  JOURNAL   DNA Res. 7, 331-338 (2000)
    """
    return {
        "refid": 1,
        "location": None,
        "notes": "sites",
        "authors": t.normalize("""
            Kaneko,T., Nakamura,Y., Sato,S., Asamizu,E., Kato,T., Sasamoto,S.,
            Watanabe,A., Idesawa,K., Ishikawa,A., Kawashima,K., Kimura,T.,
            Kishida,Y., Kiyokawa,C., Kohara,M., Matsumoto,M., Matsuno,A.,
            Mochizuki,Y., Nakayama,S., Nakazaki,N., Shimpo,S., Sugimoto,M.,
            Takeuchi,C., Yamada,M. and Tabata,S.
        """),
        "title": t.normalize("""
            Complete genome structure of the nitrogen-fixing symbiotic
            bacterium Mesorhizobium loti
        """),
        "journal": "DNA Res. 7, 331-338 (2000)"
    }

@t.parse("parse_keyword")
def test_primary_1():
    """
    PRIMARY     REFSEQ_SPAN         PRIMARY_IDENTIFIER PRIMARY_SPAN        COMP
                1-27                DA002961.1         1-27
                28-976              BC003555.1         1-949
                977-984             AW749585.1         25-32
    """
    return [
        {
            "refseq_span": {"from": 1, "to": 27},
            "primary_identifier": "DA002961.1",
            "primary_span": {"from": 1, "to": 27},
            "complement": False
        },
        {
            "refseq_span": {"from": 28, "to": 976},
            "primary_identifier": "BC003555.1",
            "primary_span": {"from": 1, "to": 949},
            "complement": False,
        },
        {
            "refseq_span": {"from": 977, "to": 984},
            "primary_identifier": "AW749585.1",
            "primary_span": {"from": 25, "to": 32},
            "complement": False
        }
    ]

@t.parse("parse_keyword")
def test_primary_2():
    """
    PRIMARY     REFSEQ_SPAN         PRIMARY_IDENTIFIER PRIMARY_SPAN        COMP
                1-635               CF172065.1         1-635
                636-2166            AC138613.6         85778-87308         c
                2167-2424           AI839133.1         1-258               c
    """
    return [
        {
            "refseq_span": {"from": 1, "to": 635},
            "primary_identifier": "CF172065.1",
            "primary_span": {"from": 1, "to": 635},
            "complement": False
        },
        {
            "refseq_span": {"from": 636, "to": 2166},
            "primary_identifier": "AC138613.6",
            "primary_span": {"from": 85778, "to": 87308},
            "complement": True,
        },
        {
            "refseq_span": {"from": 2167, "to": 2424},
            "primary_identifier": "AI839133.1",
            "primary_span": {"from": 1, "to": 258},
            "complement": True
        }
    ]

@t.parse("parse_keyword")
def test_comment():
    """
COMMENT     VALIDATED REFSEQ: This record has undergone preliminary review of
            the sequence, but has not yet been subject to final review. The
            reference sequence was derived from DA002961.1, BC003555.1,
            AW749585.1, AK225239.1 and BX645732.1.
            On Sep 27, 2007 this sequence version replaced gi:142373530.
            COMPLETENESS: complete on the 3' end.
    """
    return t.dedent("""
        VALIDATED REFSEQ: This record has undergone preliminary review of
        the sequence, but has not yet been subject to final review. The
        reference sequence was derived from DA002961.1, BC003555.1,
        AW749585.1, AK225239.1 and BX645732.1.
        On Sep 27, 2007 this sequence version replaced gi:142373530.
        COMPLETENESS: complete on the 3' end.
    """, left="\n")