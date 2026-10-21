import pytest

def test_powerset_empty_list():
    assert powerset([]) == [[]]

def test_powerset_single_element():
    assert powerset(['a']) == [[], ['a']]

def test_powerset_multiple_elements():
    assert powerset(['a', 'b', 'c']) == [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]
