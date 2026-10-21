import pytest

def test_gcd_normal_cases():
    assert gcd(35, 21) == 7
    assert gcd(100, 40) == 20
    assert gcd(81, 153) == 9

def test_gcd_boundary_case():
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5
    assert gcd(0, 0) == 0

def test_gcd_edge_cases():
    assert gcd(17, 23) == 1
    assert gcd(2 ** 31 - 1, 2 ** 31 - 1) == 2 ** 31 - 1

def test_gcd_exceptional_behavior():
    with pytest.raises(TypeError):
        gcd('a', 5)
    with pytest.raises(TypeError):
        gcd(5, 'b')
