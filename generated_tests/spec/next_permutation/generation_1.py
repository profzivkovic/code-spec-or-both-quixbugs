import pytest

def test_next_permutation_ascending():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]


def test_next_permutation_descending():
    assert next_permutation([3, 2, 1]) == [3, 1, 2]


def test_next_permutation_middle_case():
    assert next_permutation([5, 7, 6, 9, 8]) == [5, 7, 8, 6, 9]


def test_next_permutation_boundary_case():
    assert next_permutation([1, 2, 3, 4]) == [1, 2, 4, 3]


def test_next_permutation_edge_case():
    assert next_permutation([1, 3, 2]) == [2, 1, 3]


def test_next_permutation_single_element():
    assert next_permutation([5]) == [5]


def test_next_permutation_empty_list():
    with pytest.raises(ValueError):
        next_permutation([])
