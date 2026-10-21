import pytest

def test_sieve_normal_case():
    assert sieve(10) == [2, 3, 5, 7]

def test_sieve_boundary_case():
    assert sieve(2) == [2]

def test_sieve_edge_case_max_1():
    assert sieve(1) == []

def test_sieve_exceptional_behavior_non_positive_input():
    with pytest.raises(ValueError):
        sieve(-5)
