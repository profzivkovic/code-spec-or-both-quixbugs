import pytest

def test_gcd_normal_case():
    assert gcd(35, 21) == 7

def test_gcd_boundary_case_1():
    assert gcd(0, 1) == 1

def test_gcd_boundary_case_2():
    assert gcd(1, 0) == 1

def test_gcd_both_zero():
    with pytest.raises(ValueError):
        gcd(0, 0)

def test_gcd_negative_input():
    with pytest.raises(ValueError):
        gcd(-5, 3)

def test_gcd_large_numbers():
    assert gcd(123456789, 987654321) == 1
