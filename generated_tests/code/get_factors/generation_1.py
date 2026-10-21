import pytest

def test_get_factors_normal_case():
    assert get_factors(15) == [3, 5]

def test_get_factors_prime_number():
    assert get_factors(29) == [29]

def test_get_factors_one():
    assert get_factors(1) == []

def test_get_factors_square_number():
    assert get_factors(36) == [2, 18]

def test_get_factors_even_number():
    assert get_factors(40) == [2, 20]

def test_get_factors_odd_number():
    assert get_factors(75) == [3, 25]

def test_get_factors_negative_input():
    with pytest.raises(ValueError):
        get_factors(-1)

def test_get_factors_zero():
    with pytest.raises(ValueError):
        get_factors(0)