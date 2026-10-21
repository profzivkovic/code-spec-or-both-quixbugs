import pytest

def test_empty_list():
    assert mergesort([]) == []

def test_single_element():
    assert mergesort([1]) == [1]

def test_sorted_list():
    assert mergesort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_reversed_list():
    assert mergesort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_duplicates():
    assert mergesort([3, 2, 2, 1]) == [1, 2, 2, 3]

def test_random_list():
    assert mergesort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10]