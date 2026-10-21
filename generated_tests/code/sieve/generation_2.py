import pytest

def test_sieve_normal_case():
    assert sieve(10) == [2, 3, 5, 7]


def test_sieve_boundary_case():
    assert sieve(2) == [2]


def test_sieve_edge_case_empty_range():
    assert sieve(1) == []


def test_sieve_single_element_prime():
    assert sieve(3) == [2, 3]


def test_sieve_non_prime_max_value():
    assert sieve(4) == [2, 3]


def test_sieve_with_zero_and_negative_values():
    with pytest.raises(ValueError):
        sieve(-1)


def test_sieve_with_large_number():
    assert sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]
