import utils

# Test pad_list()

def test_pad_list_lower_min():
    assert utils.pad_list([1,2,3], 2, None) == [1,2,3]

def test_pad_list_equal_min():
    assert utils.pad_list([1,2,3], 3, None) == [1,2,3]

def test_pad_list_higher_min():
    assert utils.pad_list([1,2,3], 4, None) == [1,2,3, None]

# Test get_between()

def test_get_between_all_empty():
    assert utils.get_between("", "", "") == ""

def test_get_between_empty_start_and_end():
    assert utils.get_between("hello world", "", "") == "hello world"

def test_get_between_empty_start_or_end():
    assert utils.get_between("hello world", "|", "") == ""
    assert utils.get_between("hello world", "", "|") == ""

def test_get_between_same_delim_no_occurences():
    assert utils.get_between("hello world", "|", "|") == ""

def test_get_between_same_delim_one_occurence():
    assert utils.get_between("he|llo world", "|", "|") == ""

def test_get_between_same_delim_two_occurences():
    assert utils.get_between("he|ll|o world", "|", "|") == "ll"

def test_get_between_same_delim_three_occurences():
    assert utils.get_between("he|ll|o w|orld", "|", "|") == "ll"

def test_get_between_diff_delim_no_either():
    assert utils.get_between("hello world", "(", ")") == ""

def test_get_between_diff_delim_no_open():
    assert utils.get_between("hello wor)ld", "(", ")") == ""

def test_get_between_diff_delim_no_close():
    assert utils.get_between("he(llo world", "(", ")") == ""

def test_get_between_diff_delim_match():
    assert utils.get_between("he(llo wor)ld", "(", ")") == "llo wor"

def test_get_between_diff_delim_match_plus_close_before():
    assert utils.get_between("h)e(llo wor)ld", "(", ")") == "llo wor"

def test_get_between_diff_delim_match_plus_open_after():
    assert utils.get_between("he(llo wor)l(d", "(", ")") == "llo wor"

def test_get_between_diff_delim_match_plus_open_between():
    assert utils.get_between("he(llo( wor)ld", "(", ")") == "llo( wor"

# Should be consistent with test_get_between_same_delim_three_occurences
def test_get_between_diff_delim_match_plus_close_between():
    assert utils.get_between("he(llo )wor)ld", "(", ")") == "llo "

# Test get_between() with matching

def test_get_between_matching_all_empty():
    assert utils.get_between("", "", "", True) == ""

def test_get_between_matching_empty_start_and_end():
    assert utils.get_between("hello world", "", "", True) == "hello world"

def test_get_between_matching_empty_start_or_end():
    assert utils.get_between("hello world", "|", "", True) == ""
    assert utils.get_between("hello world", "", "|", True) == ""

def test_get_between_matching_same_delim_no_occurences():
    assert utils.get_between("hello world", "|", "|", True) == ""

def test_get_between_matching_same_delim_one_occurence():
    assert utils.get_between("he|llo world", "|", "|", True) == ""

def test_get_between_matching_same_delim_two_occurences():
    assert utils.get_between("he|ll|o world", "|", "|", True) == "ll"

def test_get_between_matching_same_delim_three_occurences():
    assert utils.get_between("he|ll|o w|orld", "|", "|", True) == "ll"

def test_get_between_matching_diff_delim_no_either():
    assert utils.get_between("hello world", "(", ")", True) == ""

def test_get_between_matching_diff_delim_no_open():
    assert utils.get_between("hello wor)ld", "(", ")", True) == ""

def test_get_between_matching_diff_delim_no_close():
    assert utils.get_between("he(llo world", "(", ")", True) == ""

def test_get_between_matching_diff_delim_match():
    assert utils.get_between("he(llo wor)ld", "(", ")", True) == "llo wor"

def test_get_between_matching_diff_delim_match_plus_close_before():
    assert utils.get_between("h)e(llo wor)ld", "(", ")", True) == "llo wor"

def test_get_between_matching_diff_delim_match_plus_open_after():
    assert utils.get_between("he(llo wor)l(d", "(", ")", True) == "llo wor"

def test_get_between_matching_diff_delim_match_plus_open_between():
    assert utils.get_between("he(llo( wor)ld", "(", ")", True) == ""

# Should be consistent with test_get_between_matching_same_delim_three_occurences
def test_get_between_matching_diff_delim_match_plus_close_between():
    assert utils.get_between("he(llo )wor)ld", "(", ")", True) == "llo "

# # Test get_between()

# def test_get_between_all_empty():
#     assert utils.get_between("", "", "") == ""

# def test_get_between_empty_start_and_end():
#     assert utils.get_between("hello world", "", "") == "hello world"

# def test_get_between_empty_start_or_end():
#     assert utils.get_between("hello world", "|", "") == ""
#     assert utils.get_between("hello world", "", "|") == ""

# def test_get_between_same_delim_no_occurences():
#     assert utils.get_between("hello world", "|", "|") == ""

# def test_get_between_same_delim_one_occurence():
#     assert utils.get_between("he|llo world", "|", "|") == ""

# def test_get_between_same_delim_two_occurences():
#     assert utils.get_between("he|ll|o world", "|", "|") == "ll"

# def test_get_between_same_delim_three_occurences():
#     assert utils.get_between("he|ll|o w|orld", "|", "|") == "ll"

# def test_get_between_diff_delim_no_either():
#     assert utils.get_between("hello world", "(", ")") == ""

# def test_get_between_diff_delim_no_open():
#     assert utils.get_between("hello wor)ld", "(", ")") == ""

# def test_get_between_diff_delim_no_close():
#     assert utils.get_between("he(llo world", "(", ")") == ""

# def test_get_between_diff_delim_match():
#     assert utils.get_between("he(llo wor)ld", "(", ")") == "llo wor"

# def test_get_between_diff_delim_match_plus_close_before():
#     assert utils.get_between("h)e(llo wor)ld", "(", ")") == "llo wor"

# def test_get_between_diff_delim_match_plus_open_after():
#     assert utils.get_between("he(llo wor)l(d", "(", ")") == "llo wor"

# def test_get_between_diff_delim_match_plus_open_between():
#     assert utils.get_between("he(llo( wor)ld", "(", ")") == "llo( wor"

# # Should be consistent with test_get_between_same_delim_three_occurences
# def test_get_between_diff_delim_match_plus_close_between():
#     assert utils.get_between("he(llo )wor)ld", "(", ")") == "llo "
