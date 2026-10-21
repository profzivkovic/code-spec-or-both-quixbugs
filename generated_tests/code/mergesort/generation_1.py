import pytest

def test_empty_array():
    assert mergesort([]) == [], 'Empty array should return an empty array'

def test_single_element():
    assert mergesort([5]) == [5], 'Single element array should return the same array'

def test_sorted_array():
    assert mergesort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], 'Already sorted array should remain unchanged'

def test_reverse_sorted_array():
    assert mergesort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], 'Reverse sorted array should be sorted'

def test_random_array():
    assert mergesort([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]) == [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9], 'Random array should be sorted'

def test_array_with_duplicates():
    assert mergesort([3, 3, 3, 1, 1]) == [1, 1, 3, 3, 3], 'Array with duplicates should be sorted'

def test_negative_numbers():
    assert mergesort([-5, -1, -4, -2, -3]) == [-5, -4, -3, -2, -1], 'Array with negative numbers should be sorted'
