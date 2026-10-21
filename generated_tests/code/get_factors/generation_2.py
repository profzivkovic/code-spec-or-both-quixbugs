import pytest

def test_get_factors_normal_case():
    assert get_factors(28) == [2, 14]

def test_get_factors_prime_number():
    assert get_factors(29) == []

def test_get_factors_one():
    assert get_factors(1) == []

def test_get_factors_two():
    assert get_factors(2) == [2]

def test_get_factors_large_number():
    assert get_factors(600851475143) == [71, 839, 1471, 6857]
