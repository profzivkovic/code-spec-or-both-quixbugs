import pytest

def test_powerset_empty_list():
    assert powerset([]) == [[]]

def test_powerset_single_element():
    assert powerset(['a']) == [[], ['a']]

def test_powerset_two_elements():
    assert powerset(['a', 'b']) == [[], ['b'], ['a'], ['a', 'b']]

def test_powerset_three_elements():
    assert powerset(['a', 'b', 'c']) == [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]

def test_powerset_order_of_subsets():
    result = powerset(['a', 'b', 'c'])
    expected = [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]
    assert all(subset in result for subset in expected)

def test_powerset_unique_subsets():
    result = powerset(['a', 'b', 'c'])
    assert len(result) == 8

