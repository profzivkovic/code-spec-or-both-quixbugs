import pytest

def test_powerset_empty_array():
    result = powerset([])
    assert result == [[]]

@ pytest.mark.parametrize('arr, expected', [
    ([1], [[], [1]]),
    ([1, 2], [[], [1], [2], [1, 2]]),
    ([1, 2, 3], [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]])
])
def test_powerset_with_elements(arr, expected):
    result = powerset(arr)
    assert result == expected
