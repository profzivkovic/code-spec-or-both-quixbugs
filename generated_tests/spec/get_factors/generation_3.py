import pytest

def test_get_factors_empty():
    assert get_factors(1) == []

def test_get_factors_prime():
    assert get_factors(101) == [101]

def test_get_factors_power_of_two():
    assert get_factors(16) == [2, 2, 2, 2]

def test_get_factors_product_of_primes():
    assert get_factors(35) == [5, 7]

def test_get_factors_composite_with_repeated_prime_factors():
    assert get_factors(100) == [2, 2, 5, 5]
