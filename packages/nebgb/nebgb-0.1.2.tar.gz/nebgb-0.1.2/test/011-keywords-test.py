#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_keywords")
def test_1():
    """
DEFINITION  Pseudomonas syringae pv. averrhoi strain HL1 leucyl-tRNA synthetase
            (leuS) gene, partial cds; putative lipoprotein, DNA polymerase III
            delta subunit (holA), type III effector HopAJ2 (hopAJ2), lipoic
            acid synthetase (lipA), and lipoate-protein ligase B (lipB) genes,
            complete cds; and hypothetical protein gene, partial cds.
ACCESSION   EU143250
VERSION     EU143250.1  GI:157644754
KEYWORDS    .
SOURCE      Pseudomonas syringae pv. averrhoi
  ORGANISM  Pseudomonas syringae pv. averrhoi
            Bacteria; Proteobacteria; Gammaproteobacteria; Pseudomonadales;
            Pseudomonadaceae; Pseudomonas.
REFERENCE   1  (bases 1 to 7304)
  AUTHORS   Kuo,C.-H., Lin,Y.-C. and Huang,H.-C.
  TITLE     Characterization of hopAJ1 and hopAJ2 genes from Pseudomonas
            syringae pv. averrhoi
  JOURNAL   Unpublished
REFERENCE   2  (bases 1 to 7304)
  AUTHORS   Kuo,C.-H., Lin,Y.-C. and Huang,H.-C.
  TITLE     Direct Submission
  JOURNAL   Submitted (07-SEP-2007) Graduate Institute of Biotechnology,
            National Chung Hsing University, 250 Kuo-Kuang Rd., Taichung 402,
            Taiwan
    """
    return {
        "definition": t.normalize("""
            Pseudomonas syringae pv. averrhoi strain HL1 leucyl-tRNA synthetase
            (leuS) gene, partial cds; putative lipoprotein, DNA polymerase III
            delta subunit (holA), type III effector HopAJ2 (hopAJ2), lipoic
            acid synthetase (lipA), and lipoate-protein ligase B (lipB) genes,
            complete cds; and hypothetical protein gene, partial cds       
        """),
        "accession": {"primary": "EU143250", "secondary": []},
        "version": {"accession": "EU143250.1", "gi": "157644754"},
        "keywords": [],
        "source": {
            "name": "Pseudomonas syringae pv. averrhoi",
            "organism": "Pseudomonas syringae pv. averrhoi",
            "taxonomy": """
                Bacteria Proteobacteria Gammaproteobacteria Pseudomonadales
                Pseudomonadaceae Pseudomonas
            """.split()
        },
        "reference": [{
            "refid": 1,
            "location": {"from": 1, "to": 7304},
            "notes": "",
            "authors": "Kuo,C.-H., Lin,Y.-C. and Huang,H.-C.",
            "title": t.normalize("""
                Characterization of hopAJ1 and hopAJ2 genes from Pseudomonas
                syringae pv. averrhoi
            """),
            "journal": "Unpublished"
        },{
            "refid": 2,
            "location": {"from": 1, "to": 7304},
            "notes": "",
            "authors": "Kuo,C.-H., Lin,Y.-C. and Huang,H.-C.",
            "title": "Direct Submission",
            "journal": t.normalize("""
                Submitted (07-SEP-2007) Graduate Institute of Biotechnology,
                National Chung Hsing University, 250 Kuo-Kuang Rd., Taichung 402,
                Taiwan
            """)
        }]
    }