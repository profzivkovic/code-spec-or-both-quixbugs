import pytest

def test_sieve_normal_case():
    assert sieve(10) == [2, 3, 5, 7]

def test_sieve_boundary_case():
    assert sieve(2) == [2]

def test_sieve_small_range():
    assert sieve(1) == []

def test_sieve_empty_input():
    assert sieve(0) == []

def test_sieve_prime_twice():
    assert sieve(5) == [2, 3, 5]
