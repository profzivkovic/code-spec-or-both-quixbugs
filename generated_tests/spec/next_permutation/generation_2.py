import pytest

def test_next_permutation_normal_case_1():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]

def test_next_permutation_normal_case_2():
    assert next_permutation([4, 5, 6, 7]) == [4, 5, 7, 6]

def test_next_permutation_boundary_case():
    assert next_permutation([1, 3, 2]) == [2, 1, 3]

def test_next_permutation_edge_case_single_element():
    assert next_permutation([1]) == [1]

def test_next_permutation_edge_case_reverse_sorted():
    with pytest.raises(ValueError):
        next_permutation([4, 3, 2, 1])