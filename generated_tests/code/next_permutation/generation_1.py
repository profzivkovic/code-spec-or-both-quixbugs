import pytest

def test_next_permutation():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]
    assert next_permutation([3, 2, 1]) == [1, 2, 3]
    assert next_permutation([1, 1, 5]) == [1, 5, 1]
    assert next_permutation([1, 3, 2]) == [2, 1, 3]
    with pytest.raises(ValueError) as excinfo:
        next_permutation([])
    assert 'Input list must have at least two elements' in str(excinfo.value)
