import pytest

def test_powerset_empty_set():
    assert powerset([]) == [[]]

def test_powerset_single_element():
    assert powerset(['a']) == [[], ['a']]

def test_powerset_two_elements():
    assert powerset(['a', 'b']) == [[], ['b'], ['a'], ['a', 'b']]

def test_powerset_three_elements():
    assert powerset(['a', 'b', 'c']) == [[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]

