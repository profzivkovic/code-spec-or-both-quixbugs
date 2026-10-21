import pytest

def test_sieve_normal_cases():
    assert sieve(10) == [2, 3, 5, 7]
    assert sieve(1) == []
    assert sieve(2) == [2]


def test_sieve_boundary_cases():
    assert sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert sieve(50) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def test_sieve_edge_cases():
    assert sieve(0) == []
    assert sieve(-5) == []


def test_sieve_exceptional_behavior():
    with pytest.raises(TypeError):
        sieve('a')
