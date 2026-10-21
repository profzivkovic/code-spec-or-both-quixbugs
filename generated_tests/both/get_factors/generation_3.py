import pytest

def test_get_factors_empty_list_for_one():
    assert get_factors(1) == []

def test_get_factors_prime_number():
    assert get_factors(101) == [101]

def test_get_factors_power_of_two():
    assert get_factors(16) == [2, 2, 2, 2]

def test_get_factors_power_of_three():
    assert get_factors(27) == [3, 3, 3]

def test_get_factors_product_of_two_primes():
    assert get_factors(15) == [3, 5]

def test_get_factors_product_of_three_primes():
    assert get_factors(105) == [3, 5, 7]

def test_get_factors_large_number():
    assert get_factors(987654321) == [3, 3, 3, 3607, 9817]
