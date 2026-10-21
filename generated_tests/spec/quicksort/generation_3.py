import pytest

def test_quicksort_empty_array():
    assert quicksort([]) == [], 'Empty array should return an empty array'


def test_quicksort_single_element():
    assert quicksort([5]) == [5], 'Single element array should remain unchanged'


def test_quicksort_sorted_array():
    assert quicksort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], 'Already sorted array should remain unchanged'


def test_quicksort_reverse_sorted_array():
    assert quicksort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], 'Reverse sorted array should be sorted'


def test_quicksort_random_array():
    assert quicksort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10], 'Random array should be sorted'


def test_quicksort_array_with_duplicates():
    assert quicksort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10], 'Array with duplicates should be sorted'
