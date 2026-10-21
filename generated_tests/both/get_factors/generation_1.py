import pytest

def test_get_factors_1():
    assert get_factors(1) == []

def test_get_factors_2():
    assert get_factors(2) == [2]

def test_get_factors_4():
    assert get_factors(4) == [2, 2]

def test_get_factors_5():
    assert get_factors(5) == [5]

def test_get_factors_6():
    assert get_factors(6) == [2, 3]

def test_get_factors_100():
    assert get_factors(100) == [2, 2, 5, 5]

def test_get_factors_101():
    assert get_factors(101) == [101]

