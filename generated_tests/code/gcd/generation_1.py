import pytest

def test_gcd_normal_cases():
    assert gcd(48, 18) == 6
    assert gcd(100, 25) == 25
    assert gcd(7, 13) == 1

def test_gcd_boundary_cases():
    assert gcd(0, 1) == 1
    assert gcd(1, 0) == 1

def test_gcd_negative_numbers():
    assert gcd(-48, 18) == 6
    assert gcd(48, -18) == 6
    assert gcd(-48, -18) == 6

def test_gcd_zero_input():
    with pytest.raises(ValueError):
        gcd(0, 0)
