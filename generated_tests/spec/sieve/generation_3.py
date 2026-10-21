import pytest

def test_sieve_normal_case():
    assert sieve(10) == [2, 3, 5, 7]

def test_sieve_boundary_case():
    assert sieve(2) == [2]

def test_sieve_edge_case():
    assert sieve(1) == []

def test_sieve_prime_at_boundary():
    assert sieve(19) == [2, 3, 5, 7, 11, 13, 17, 19]

def test_sieve_no_primes():
    assert sieve(0) == []

def test_sieve_single_prime():
    assert sieve(3) == [2, 3]

def test_sieve_all_composites():
    assert sieve(4) == [2, 3]

def test_sieve_max_is_1():
    assert sieve(1) == []
