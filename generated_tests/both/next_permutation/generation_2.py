import pytest

def test_next_permutation_ascending():
    perm = [1, 2, 3]
    assert next_permutation(perm) == [1, 3, 2]

def test_next_permutation_descending():
    perm = [3, 2, 1]
    with pytest.raises(ValueError):
        next_permutation(perm)

def test_next_permutation_boundary_case():
    perm = [1]
    assert next_permutation(perm) == [1]

def test_next_permutation_edge_case():
    perm = [2, 3, 1]
    assert next_permutation(perm) == [3, 1, 2]

def test_next_permutation_repeated_elements():
    perm = [1, 1, 2]
    with pytest.raises(ValueError):
        next_permutation(perm)
