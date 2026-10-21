import pytest

def test_next_permutation_normal_case():
    assert next_permutation([3, 2, 4, 1]) == [3, 4, 1, 2]

def test_next_permutation_boundary_case():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]

def test_next_permutation_edge_case():
    assert next_permutation([1, 3, 2]) == [2, 1, 3]

def test_next_permutation_reverse_sorted_case():
    with pytest.raises(ValueError):
        next_permutation([4, 3, 2, 1])