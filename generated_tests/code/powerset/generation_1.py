import pytest

def test_powerset_empty_list():
    assert powerset([]) == [[]]

def test_powerset_single_element():
    assert powerset([1]) == [[], [1]]

def test_powerset_multiple_elements():
    assert powerset([1, 2]) == [[], [2], [1], [1, 2]]

def test_powerset_duplicate_elements():
    assert powerset([1, 1]) == [[], [1], [1, 1]]