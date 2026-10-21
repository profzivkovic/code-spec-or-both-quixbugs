import pytest

def test_gcd_normal_cases():
    assert gcd(48, 18) == 6
    assert gcd(20, 5) == 5
    assert gcd(7, 3) == 1


def test_gcd_boundary_cases():
    assert gcd(0, 1) == 1
    assert gcd(1, 0) == 1
    assert gcd(0, 0) == 0


def test_gcd_edge_cases():
    assert gcd(-48, -18) == 6
    assert gcd(48, -18) == 6
    assert gcd(-48, 18) == 6


def test_gcd_exceptional_behavior():
    with pytest.raises(TypeError):
        gcd('a', 5)
    with pytest.raises(TypeError):
        gcd(5, 'b')
    with pytest.raises(TypeError):
        gcd('a', 'b')