import pytest

def test_get_factors_normal_cases():
    assert get_factors(1) == []
    assert get_factors(2) == [2]
    assert get_factors(3) == [3]
    assert get_factors(4) == [2, 2]
    assert get_factors(5) == [5]
    assert get_factors(6) == [2, 3]
    assert get_factors(7) == [7]
    assert get_factors(8) == [2, 2, 2]
    assert get_factors(9) == [3, 3]
    assert get_factors(10) == [2, 5]
    assert get_factors(25) == [5, 5]


def test_get_factors_prime_numbers():
    assert get_factors(101) == [101]
    assert get_factors(97) == [97]


def test_get_factors_even_and_odd_cases():
    assert get_factors(2 * 3 * 5) == [2, 3, 5]
    assert get_factors(2 * 2 * 3 * 3 * 5 * 5) == [2, 2, 3, 3, 5, 5]


def test_get_factors_power_cases():
    assert get_factors(7**3) == [7, 7, 7]


def test_get_factors_mixed_cases():
    assert get_factors(2 * 3 * 11) == [2, 3, 11]
    assert get_factors(2 * 5 * 7 * 11) == [2, 5, 7, 11]