import pytest

def test_empty_array():
    assert mergesort([]) == []

def test_single_element():
    assert mergesort([1]) == [1]

def test_sorted_array():
    assert mergesort([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_reverse_sorted_array():
    assert mergesort([4, 3, 2, 1]) == [1, 2, 3, 4]

def test_random_array():
    assert mergesort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]
