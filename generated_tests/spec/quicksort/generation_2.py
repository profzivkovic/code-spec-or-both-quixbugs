import pytest

def test_quicksort_normal_case():
    assert quicksort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10]

def test_quicksort_boundary_case_single_element():
    assert quicksort([5]) == [5]

def test_quicksort_boundary_case_empty_list():
    assert quicksort([]) == []

def test_quicksort_edge_case_sorted_list():
    assert quicksort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_quicksort_edge_case_reverse_sorted_list():
    assert quicksort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_quicksort_exceptional_behavior_duplicate_values():
    assert quicksort([3, 6, 8, 10, 1, 2, 1, 6]) == [1, 1, 2, 3, 6, 6, 8, 10]
