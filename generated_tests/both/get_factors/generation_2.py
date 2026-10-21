import pytest

def test_get_factors_empty_list():
    assert get_factors(1) == []

def test_get_factors_prime_number():
    assert get_factors(101) == [101]

def test_get_factors_power_of_two():
    assert get_factors(32) == [2, 2, 2, 2, 2]

def test_get_factors_even_number():
    assert get_factors(44) == [2, 2, 11]

def test_get_factors_odd_number():
    assert get_factors(75) == [3, 5, 5]

def test_get_factors_large_number():
    assert get_factors(987654321) == [3, 3, 3, 3607, 982451]