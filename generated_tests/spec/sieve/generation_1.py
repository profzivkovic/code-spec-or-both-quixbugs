import pytest

def test_sieve_empty_input():
    assert sieve(0) == []
    assert sieve(-1) == []


def test_sieve_single_prime():
    assert sieve(2) == [2]


def test_sieve_multiple_primes():
    assert sieve(10) == [2, 3, 5, 7]
    assert sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]


def test_sieve_no_primes():
    assert sieve(1) == []
    assert sieve(4) == [2, 3]
