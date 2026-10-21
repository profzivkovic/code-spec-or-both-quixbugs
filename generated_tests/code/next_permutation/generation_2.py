import pytest

def test_next_permutation_normal_cases():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]
    assert next_permutation([1, 3, 2]) == [2, 1, 3]
    assert next_permutation([3, 2, 1]) is None
    assert next_permutation([1, 2, 4, 3]) == [1, 3, 2, 4]

def test_next_permutation_boundary_cases():
    assert next_permutation([1]) is None
    assert next_permutation([]) is None

def test_next_permutation_edge_cases():
    assert next_permutation([1, 1, 1]) == [1, 1, 1]

def test_next_permutation_exceptional_behavior():
    with pytest.raises(TypeError):
        next_permutation('abc')
