import pytest

def test_empty_set():
    assert powerset([]) == [[]]

def test_single_element_set():
    assert powerset([1]) == [[], [1]]

def test_two_elements_set():
    assert powerset(['a', 'b']) == [[], ['b'], ['a'], ['a', 'b']]

def test_three_elements_set():
    assert powerset(['a', 'b', 'c']) == [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]

def test_order_of_subsets():
    subsets = powerset([1, 2, 3])
    expected = [[], [3], [2], [2, 3], [1], [1, 3], [1, 2], [1, 2, 3]]
    assert subsets == expected

def test_duplicate_elements():
    with pytest.raises(ValueError):
        powerset([1, 1])
