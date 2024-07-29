import pytest
from src.closest_coding_seq import find_closest_coding_seq, update_name, decrement_field


# test cases
# 1: test when given allele name is complete
# 2: test going from hundred to tens
# 3: test when ending on allele name with letter
# 4: test given allele name with letter is complete
# 5: test when decrimenting second field/adding another field
# 6: test when decrimenting last field
def test_one(allele_name, allele_data1, allele_data2, allele_data3, expected):
    assert find_closest_coding_seq(allele_name[0], allele_data1) == expected[0]
    assert find_closest_coding_seq(allele_name[1], allele_data1) == expected[1]
    assert find_closest_coding_seq(allele_name[2], allele_data2) == expected[2]
    assert find_closest_coding_seq(allele_name[3], allele_data2) == expected[3]
    assert find_closest_coding_seq(allele_name[4], allele_data3) == expected[4]
    assert find_closest_coding_seq(allele_name[5], allele_data3) == expected[5]

# tests for decrement field
def test_decrement_field():
    assert decrement_field("A*02:01:10") == "A*02:01:09"
    assert decrement_field("A*02:01:09") == "A*02:01:08"
    assert decrement_field("A*02:01:08") == "A*02:01:07"
    assert decrement_field("A*02:01:101") == "A*02:01:100"
    assert decrement_field("A*02:01:100") == "A*02:01:99"
    assert decrement_field("A*02:01:1000") == "A*02:01:999"



# tests for update name
def test_update_name(allele_data1, allele_data2, allele_data3):
    assert update_name("A*02:07:107", allele_data1) == "A*02:07:106"
    assert update_name('A*02:07:100', allele_data1) == "A*02:07:99"
    assert update_name('A*02:06:15', allele_data2) == "A*02:06:14N"
    assert update_name('A*02:06:14N', allele_data2) == "A*02:06:13"
    assert update_name('A*02:06:02', allele_data3) == 'A*02:06:01:03'
    assert update_name('A*02:06:01:01', allele_data3) == 'A*02:05:06'