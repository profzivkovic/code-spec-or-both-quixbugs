import pytest

def test_gcd_normal_cases():
    assert gcd(35, 21) == 7
    assert gcd(100, 25) == 25
    assert gcd(81, 27) == 27
    assert gcd(17, 13) == 1

def test_gcd_boundary_cases():
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5
    assert gcd(0, 0) == 0

def test_gcd_edge_cases():
    assert gcd(1, 1) == 1

def test_gcd_exceptional_behavior():
    with pytest.raises(TypeError):
        gcd('a', 2)
    with pytest.raises(TypeError):
        gcd(2, 'b')