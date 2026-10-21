import pytest

def test_mergesort_empty_array():
    assert mergesort([]) == [], 'Empty array should return an empty array'


def test_mergesort_single_element():
    assert mergesort([5]) == [5], 'Single element array should return the same array'


def test_mergesort_sorted_array():
    assert mergesort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], 'Already sorted array should remain unchanged'


def test_mergesort_reversed_array():
    assert mergesort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], 'Reversed array should be sorted'


def test_mergesort_random_array():
    assert mergesort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9], 'Random array should be sorted'


def test_mergesort_array_with_duplicates():
    assert mergesort([3, 3, 2, 1, 5, 3, 2]) == [1, 2, 2, 3, 3, 3, 5], 'Array with duplicates should be sorted'


def test_mergesort_array_with_negative_numbers():
    assert mergesort([-3, -1, -4, -1, -5, -9, -2, -6]) == [-9, -6, -5, -4, -3, -2, -1, -1], 'Array with negative numbers should be sorted'
