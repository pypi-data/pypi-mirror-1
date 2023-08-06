
nebgb - Genbank File Parser
===========================

Usage:

    >>> import nebgb
    >>> rec = nebgb.parse_file("./test/data/simple-1.gb").next()
    >>> rec.locus["name"]
    'NP_034640'
    >>> rec.locus["length"]
    182
    >>> rec.keywords["source"]["name"]
    'house mouse'
    >>> rec.features[1]["properties"]["product"]
    'interferon beta, fibroblast'
    >>> for seq in rec.seqiter:
    ...    print seq
    mnnrwilhaafllcfsttalsinykqlqlqertnirkcqelleqlngkinltyradfkip
    memtekmqksytafaiqemlqnvflvfrnnfsstgwnetivvrlldelhqqtvflktvle
    ekqeerltwemsstalhlksyywrvqrylklmkynsyawmvvraeifrnfliirrltrnf
    qn

Alternatively you can use `nebgb.parse()` to parse a string or iterator that yields lines of a Genbank file. 
