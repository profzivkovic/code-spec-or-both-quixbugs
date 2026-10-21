import pytest

def test_sieve_small_input():
    assert sieve(5) == [2, 3, 5]


def test_sieve_boundary_case():
    assert sieve(2) == [2]


def test_sieve_single_element_case():
    assert sieve(1) == []


def test_sieve_empty_input():
    assert sieve(0) == []


def test_sieve_large_input():
    assert sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]


def test_sieve_with_non_prime_max():
    assert sieve(10) == [2, 3, 5, 7]


def test_sieve_with_one_and_zero():
    assert sieve(1) == []
    assert sieve(0) == []