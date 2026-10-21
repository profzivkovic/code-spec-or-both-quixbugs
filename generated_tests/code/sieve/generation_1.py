import pytest

def test_sieve_normal_case():
    assert sieve(10) == [2, 3, 5, 7]


def test_sieve_boundary_case():
    assert sieve(2) == [2]


def test_sieve_edge_case_zero_input():
    assert sieve(0) == []


def test_sieve_negative_input():
    with pytest.raises(ValueError):
        sieve(-1)
