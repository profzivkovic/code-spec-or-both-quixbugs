import pytest

def test_mergesort_normal_case():
    assert mergesort([34, 7, 23, 32, 5, 62]) == [5, 7, 23, 32, 34, 62]

def test_mergesort_boundary_case_empty_list():
    assert mergesort([]) == []

def test_mergesort_boundary_case_single_element():
    assert mergesort([5]) == [5]

def test_mergesort_edge_case_reverse_sorted():
    assert mergesort([64, 34, 25, 12, 22, 11, 90]) == [11, 12, 22, 25, 34, 64, 90]

def test_mergesort_edge_case_already_sorted():
    assert mergesort([11, 12, 22, 25, 34, 64, 90]) == [11, 12, 22, 25, 34, 64, 90]

def test_mergesort_edge_case_duplicates():
    assert mergesort([5, 7, 23, 32, 5, 62]) == [5, 5, 7, 23, 32, 62]
