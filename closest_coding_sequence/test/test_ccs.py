import pytest
from src.closest_coding_seq import find_closest_coding_seq, update_name, decrement_field

allele_data1 = {
    'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA',
    'A*02:07:99': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:07:100': "*ACGTCAGAATAGCAGGATACT...*.********" ,
    'A*02:07:101': "ACGTCAGAATAGCAGGATACT...*.*********" ,
    'A*02:07:102': "ACGTCAGAATAGCAGGATACT...*.*********" ,
    'A*02:07:103': "*ACGTCAGAATAGCAGGATACT...*.********" ,
    'A*02:07:104': "*ACGTCAGAATAGCAGGATACT...*.********" ,
    'A*02:07:105': "ACGTCAGAATAGCAGGATACT...*.*******" ,
    'A*02:07:106': "*********************...*.*******" ,
    'A*02:07:107': "*********************...*.*******" 
}

allele_data2 = {
    'A*02:06:08': "**" ,
    'A*02:06:09N': "ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
    'A*02:06:10': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:11': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:12': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:13': "**ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
    'A*02:06:14N': "*ACGTCAGAATAGCAGGATACT...G.CCGTATA*" ,
    'A*02:06:15': "**ACGTCAGAATAGCAGGATACT...G.CCGTATA" ,
}

allele_data3 = { 
    'A*01:03:01': "ACGTCAGAATAGCAGGATACT...G.CCGTATA", 
    'A*02:01:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:02:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:03:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:04:01': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:01':"*ACGTCAGAATAGCAGGATACT...C.********",
    'A*02:05:02': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:03':"*ACGTCAGAATAGCAGGATACT...C.********",
    'A*02:05:04': "ACGTCAGAATAGCAGGATACT...C.",
    'A*02:05:05': "*ACGTCAGAATAGCAGGATACT...C.********", 
    'A*02:05:06':"*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:01:01': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:01:02':"ACGTCAGAATAGCAGGATACT...C.*********" ,
    'A*02:06:01:03': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:02': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:03': "*ACGTCAGAATAGCAGGATACT...C.********" ,
    'A*02:06:04': "**ACGTCAGAATAGCAGGATACT...C.*******" ,
    'A*02:06:05': "*ACGTCAGAATAGCAGGATACT...C.********" ,
}

allele_data4 = { 
    'A*01:03:01': "*ACGTCAGAATAGCAGGATACT...C.", 
    'A*02:01:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:02:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:03:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:04:01': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:01':"*ACGTCAGAATAGCAGGATACT...C.*",
    'A*02:05:02': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:03':"*ACGTCAGAATAGCAGGATACT...C.*",
    'A*02:05:04': "*ACGTCAGAATAGCAGGATACT...C.",
    'A*02:05:05': "*ACGTCAGAATAGCAGGATACT...C.*", 
    'A*02:05:06':"*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:01:01': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:01:02':"ACGTCAGAATAGCAGGATACT...C.**" ,
    'A*02:06:01:03': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:02': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:03': "*ACGTCAGAATAGCAGGATACT...C.*" ,
    'A*02:06:04': "**ACGTCAGAATAGCAGGATACT...C." ,
    'A*02:06:05': "*ACGTCAGAATAGCAGGATACT...C.*" ,
}

# test cases
# 1: test when given allele name is complete
# 2: test going from hundred to tens
# 3: test when ending on allele name with letter
# 4: test given allele name with letter is complete
# 5: test when given name is not in data
# 6: test when decrimenting second field/adding another field
# 7: test when decrimenting last field
# 8: test when there are no complete sequences
@pytest.mark.parametrize("allele_name, allele_data, expected", [
    ("A*02:07:107", allele_data1, {'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}),
    ("A*02:07:98", allele_data1, {'A*02:07:98': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}),
    ("A*02:06:15", allele_data2, {'A*02:06:09N': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}),
    ("A*02:06:09N", allele_data2, {'A*02:06:09N': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}),
    # ("A*02:07:107", allele_data2, {}),
    ("A*02:06:05", allele_data3, {'A*02:05:04': 'ACGTCAGAATAGCAGGATACT...C.'}),
    ("A*02:05:03", allele_data3, {'A*01:03:01': 'ACGTCAGAATAGCAGGATACT...G.CCGTATA'}),
    # ("A*02:06:05", allele_data4, {})
])

def test_ccs(allele_name, allele_data, expected):
    assert find_closest_coding_seq(allele_name, allele_data) == expected

# tests for decrement field
def test_decrement_field():
    assert decrement_field("A*02:01:10") == "A*02:01:09"
    assert decrement_field("A*02:01:09") == "A*02:01:08"
    assert decrement_field("A*02:01:08") == "A*02:01:07"
    assert decrement_field("A*02:01:101") == "A*02:01:100"
    assert decrement_field("A*02:01:100") == "A*02:01:99"
    assert decrement_field("A*02:01:1000") == "A*02:01:999"



# tests for update name
def update_name_test():
    assert update_name("A*02:07:107", allele_data1) == "A*02:07:106"
    assert update_name('A*02:07:100', allele_data1) == "A*02:07:99"
    assert update_name('A*02:06:15', allele_data2) == "A*02:06:14N"
    assert update_name('A*02:06:14N', allele_data2) == "A*02:06:13"
    assert update_name('A*02:06:02', allele_data3) == 'A*02:06:01:03'
    assert update_name('A*02:06:01:01', allele_data3) == 'A*02:05:06'