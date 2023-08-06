#
# Copyright 2009 New England Biolabs <davisp@neb.com>
#
# This file is part of the nebgb package released under the MIT license.
#

import t

def test_1():
    data = """
        1 cacaggccca gagccactcc tgcctacagg ttctgagggc tcaggggacc tcctgggccc
       61 tcaggctctt tagctgagaa taagggccct gagggaacta cctgcttctc acatccccgg
      121 gtctctgacc atctgctgtg tgccccgacc ccccctaccc tgctcctcca ccaagcctga
      181 tgccaagggc tataaaccac tggcccaaca gaagcttggt tcccagagaa ctggtccctg
      241 cctgggacat gctccttgct acagcccctt gtgggagctc agagggcatg gctgctcccc
      301 ctacggtccc tcgcccagtg gttctgtctc tttatggcag gaagcaatga ggctccccaa
      361 gaacacacct gaggaaaagg acaggtgagc ctggagggcc ggccgcaccg tgggcctctg
      421 tgtctgggga gttggtggcc aggatcccga gtacctgggt gctgtgacgg ggcgtggttg
      481 gcctgggcgt gctgggtgtt tgggaatgac ttcccatcgc ccgcttctgc agcctgctca
      541 gccctgttgg ggtgcagtgt gtccactgcc tgcctgtgtg tgccgctgtg ctcaggctct
      601 cctcttgctc ctttcaggcg cacggcggcc ctacaggagg gtctgaggcg ggcagtctct
      661 gtgccgctga cgctggcgga gacggtggcc tcgctgtggc cggccctgca ggaactggcc
      721 cggtgtggga acctggcctg ccggtcagac ctccaggtag gggggcccgg gggaccccag
      781 gcctcctgcc gcaaagcagg aagcagctgt tggggctgag ttgctggaga gcacggtggt
      841 tggctgggct gagccaggta gggagacctc acttcacggg cagttcccgg ggctttggcc
      901 tcctccaaca gggccggggt gtccgctgcc ttctaagatc tcgctcacgg cggcaccaca
      961 gacggagacc caaatgtgtc tgcagagccc accctgacca ctgtataagt gtatactccc
     1021 ccaagacccc ttgtatcacc cccactgtcg tgttctagaa aacacctatg tcagcccagg
     1081 cacaatggtt ctcgcctgtg gtcccagcac tttgggaggc tgaggcggga ggatcacttg
     1141 aatagaggag gtcgagacca gcctgggcaa catagtggga ccctggctgt acaatagata
     1201 catatgagcc aggcacggtg gtgcctgtgg tcccagctcc ctgcccagcc agcctcctgt
     1261 ctccagagaa gttctccatt aaaaaataat ttagcaaaaa aaaaaaaaaa aaaaaaaaaa
     1321 aaaaaa
//
    """.lstrip("\n")
    reader = t.nebgb.Reader.from_string(data)
    seqiter = t.nebgb.Sequence(reader)
    expiter = iter([
        "cacaggcccagagccactcctgcctacaggttctgagggctcaggggacctcctgggccc",
        "tcaggctctttagctgagaataagggccctgagggaactacctgcttctcacatccccgg",
        "gtctctgaccatctgctgtgtgccccgaccccccctaccctgctcctccaccaagcctga",
        "tgccaagggctataaaccactggcccaacagaagcttggttcccagagaactggtccctg",
        "cctgggacatgctccttgctacagccccttgtgggagctcagagggcatggctgctcccc",
        "ctacggtccctcgcccagtggttctgtctctttatggcaggaagcaatgaggctccccaa",
        "gaacacacctgaggaaaaggacaggtgagcctggagggccggccgcaccgtgggcctctg",
        "tgtctggggagttggtggccaggatcccgagtacctgggtgctgtgacggggcgtggttg",
        "gcctgggcgtgctgggtgtttgggaatgacttcccatcgcccgcttctgcagcctgctca",
        "gccctgttggggtgcagtgtgtccactgcctgcctgtgtgtgccgctgtgctcaggctct",
        "cctcttgctcctttcaggcgcacggcggccctacaggagggtctgaggcgggcagtctct",
        "gtgccgctgacgctggcggagacggtggcctcgctgtggccggccctgcaggaactggcc",
        "cggtgtgggaacctggcctgccggtcagacctccaggtaggggggcccgggggaccccag",
        "gcctcctgccgcaaagcaggaagcagctgttggggctgagttgctggagagcacggtggt",
        "tggctgggctgagccaggtagggagacctcacttcacgggcagttcccggggctttggcc",
        "tcctccaacagggccggggtgtccgctgccttctaagatctcgctcacggcggcaccaca",
        "gacggagacccaaatgtgtctgcagagcccaccctgaccactgtataagtgtatactccc",
        "ccaagaccccttgtatcacccccactgtcgtgttctagaaaacacctatgtcagcccagg",
        "cacaatggttctcgcctgtggtcccagcactttgggaggctgaggcgggaggatcacttg",
        "aatagaggaggtcgagaccagcctgggcaacatagtgggaccctggctgtacaatagata",
        "catatgagccaggcacggtggtgcctgtggtcccagctccctgcccagccagcctcctgt",
        "ctccagagaagttctccattaaaaaataatttagcaaaaaaaaaaaaaaaaaaaaaaaaa",
        "aaaaaa"
    ])
    t.samesequence(seqiter, expiter)

def test_2():
    data = """
        1 meecwvteia ngskdgldsn pmkdymilsg pqktavavlc tllgllsale nvavlylils
       61 shqlrrkpsy lfigslagad flasvvfacs fvnfhvfhgv dskavfllki gsvtmtftas
      121 vgsllltaid rylclrypps ykalltrgra lvtlgimwvl salvsylplm gwtccprpcs
      181 elfplipndy llswllfiaf lfsgiiytyg hvlwkahqhv aslsghqdrq vpgmarmrld
      241 vrlaktlglv lavllicwfp vlalmahsla ttlsdqvkka fafcsmlcli nsmvnpviya
      301 lrsgeirssa hhclahwkkc vrglgseake eaprssvtet eadgkitpwp dsrdldlsdc
      361 
//
    """.lstrip("\n")
    reader = t.nebgb.Reader.from_string(data)
    seqiter = t.nebgb.Sequence(reader)
    expiter = iter([
        "meecwvteiangskdgldsnpmkdymilsgpqktavavlctllgllsalenvavlylils",
        "shqlrrkpsylfigslagadflasvvfacsfvnfhvfhgvdskavfllkigsvtmtftas",
        "vgsllltaidrylclryppsykalltrgralvtlgimwvlsalvsylplmgwtccprpcs",
        "elfplipndyllswllfiaflfsgiiytyghvlwkahqhvaslsghqdrqvpgmarmrld",
        "vrlaktlglvlavllicwfpvlalmahslattlsdqvkkafafcsmlclinsmvnpviya",
        "lrsgeirssahhclahwkkcvrglgseakeeaprssvteteadgkitpwpdsrdldlsdc"
    ])
    t.samesequence(seqiter, expiter)
    
