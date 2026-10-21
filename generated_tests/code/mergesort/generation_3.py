import pytest

def test_mergesort_empty_array():
    assert mergesort([]) == [], 'Empty array should be sorted to an empty array'

def test_mergesort_single_element_array():
    assert mergesort([5]) == [5], 'Single element array should remain unchanged'

def test_mergesort_sorted_array():
    assert mergesort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], 'Already sorted array should remain unchanged'

def test_mergesort_reverse_sorted_array():
    assert mergesort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], 'Reverse sorted array should be sorted'

def test_mergesort_random_array():
    assert mergesort([3, 1, 4, 1, 5, 9, 2, 6, 5]) == [1, 1, 2, 3, 4, 5, 5, 6, 9], 'Random array should be sorted'

def test_mergesort_array_with_duplicates():
    assert mergesort([3, 3, 3, 3]) == [3, 3, 3, 3], 'Array with duplicates should remain unchanged'
