import pytest

def test_gcd_normal_case_1():
    assert gcd(35, 21) == 7

def test_gcd_normal_case_2():
    assert gcd(100, 25) == 25

def test_gcd_boundary_case_1():
    assert gcd(0, 5) == 5

def test_gcd_boundary_case_2():
    assert gcd(5, 0) == 5

def test_gcd_boundary_case_3():
    assert gcd(0, 0) == 0

def test_gcd_odd_numbers():
    assert gcd(17, 13) == 1

def test_gcd_even_numbers():
    assert gcd(48, 18) == 6
