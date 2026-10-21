import pytest

def test_gcd_normal_cases():
    assert gcd(35, 21) == 7
    assert gcd(48, 18) == 6
    assert gcd(100, 25) == 25

def test_gcd_boundary_case():
    assert gcd(0, 5) == 5
    assert gcd(7, 0) == 7

def test_gcd_edge_cases():
    assert gcd(1, 1) == 1
    assert gcd(2, 3) == 1

def test_gcd_exceptional_behavior():
    with pytest.raises(TypeError):
        gcd('a', 5)
    with pytest.raises(TypeError):
        gcd(5, 'b')