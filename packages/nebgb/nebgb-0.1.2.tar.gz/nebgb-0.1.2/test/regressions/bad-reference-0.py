
def test_name(rec):
    assert rec.locus["name"] == "NC_008512"

def test_reference(rec):
    assert rec.keywords["reference"][0] == {
        'title': 'The 160-kilobase genome of the bacterial endosymbiont Carsonella',
        'journal': 'Science 314 (5797), 267 (2006)',
        'refid': 1,
        'pubmed': '17038615',
        'location': None,
        'notes': ''
    }
