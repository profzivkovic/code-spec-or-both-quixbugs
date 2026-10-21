import pytest

def test_next_permutation_normal_case():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]

def test_next_permutation_boundary_case():
    assert next_permutation([3, 2, 1]) == [1, 2, 3]

def test_next_permutation_edge_case():
    assert next_permutation([1, 1, 5]) == [1, 5, 1]

def test_next_permutation_repetitive_elements():
    assert next_permutation([2, 2, 2]) == [2, 2, 2]

def test_next_permutation_single_element():
    assert next_permutation([5]) == [5]
