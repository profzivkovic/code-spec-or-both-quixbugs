import pytest

def test_get_factors_empty():
    assert get_factors(1) == [], "Expected an empty list for input 1"

def test_get_factors_small_prime():
    assert get_factors(101) == [101], "Expected [101] for input 101"

def test_get_factors_large_number():
    assert get_factors(100) == [2, 2, 5, 5], "Expected [2, 2, 5, 5] for input 100"
