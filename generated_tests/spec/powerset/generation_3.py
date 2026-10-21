import pytest

def test_empty_set():
    assert powerset([]) == [[]]

def test_single_element_set():
    assert powerset(['a']) == [[], ['a']]

def test_two_elements_set():
    assert powerset(['a', 'b']) == [[], ['b'], ['a'], ['a', 'b']]

def test_three_elements_set():
    assert powerset(['a', 'b', 'c']) == [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]

# Test for edge cases and exceptional behavior

def test_empty_list_exception():
    with pytest.raises(ValueError):
        powerset(None)

def test_non_list_input_exception():
    with pytest.raises(TypeError):
        powerset('not a list')
