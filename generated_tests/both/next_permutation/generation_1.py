import pytest

def test_next_permutation():
    assert next_permutation([3, 2, 4, 1]) == [3, 4, 1, 2]
    assert next_permutation([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    assert next_permutation([1, 2, 3]) == [1, 3, 2]
    assert next_permutation([6, 7, 8, 9, 10]) == [6, 7, 8, 10, 9]
    assert next_permutation([4, 3, 2, 1]) is None
    assert next_permutation([]) is None