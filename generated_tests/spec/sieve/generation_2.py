import pytest

def test_sieve_empty_input():
    assert sieve(0) == [], 'Empty input should return an empty list'

def test_sieve_single_prime():
    assert sieve(2) == [2], 'Single prime number should return a list containing that number'

def test_sieve_multiple_primes():
    assert sieve(10) == [2, 3, 5, 7], 'Multiple primes up to 10 should be correctly identified'

def test_sieve_with_zero():
    assert sieve(0) == [], 'Input of zero should return an empty list'

def test_sieve_with_negative_input():
    with pytest.raises(ValueError):
        sieve(-5), 'Negative input should raise a ValueError'

def test_sieve_with_one():
    assert sieve(1) == [], 'Input of one should return an empty list'
