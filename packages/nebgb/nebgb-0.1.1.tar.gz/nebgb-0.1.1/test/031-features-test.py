#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

@t.parse("parse_features")
def test_multiple_features():
    """
     source          1..182
                     /organism="Mus musculus"
                     /db_xref="taxon:10090"
                     /chromosome="4"
                     /map="4 42.6 cM"
     Protein         1..182
                     /product="interferon beta, fibroblast"
     sig_peptide     1..21
     Region          1..182
                     /region_name="Interferon alpha/beta domain"
                     /db_xref="CDD:pfam00143"
                     /note="interferon"
     mat_peptide     22..182
                     /product="ifn-beta"
     Region          56..170
                     /region_name="Interferon alpha, beta and delta."
                     /db_xref="CDD:IFabd"
                     /note="IFabd"
     CDS             1..182
                     /gene="Ifnb"
                     /db_xref="LocusID:15977"
                     /db_xref="MGD:MGI:107657"
                     /coded_by="NM_010510.1:21..569"
    """
    return [
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
            "properties": {"product": "interferon beta, fibroblast"}
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
            "properties": {"product": "ifn-beta"}
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
