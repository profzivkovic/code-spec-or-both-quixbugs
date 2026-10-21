import pytest

def test_gcd_normal_case_1():
    assert gcd(35, 21) == 7

def test_gcd_normal_case_2():
    assert gcd(0, 5) == 5

def test_gcd_normal_case_3():
    assert gcd(18, 48) == 6

def test_gcd_boundary_case_1():
    assert gcd(0, 0) == 0

def test_gcd_boundary_case_2():
    assert gcd(1, 1) == 1

def test_gcd_edge_case_1():
    assert gcd(100, 0) == 100

def test_gcd_edge_case_2():
    assert gcd(0, 100) == 100

def test_gcd_exceptional_behavior_1():
    with pytest.raises(TypeError):
        gcd('a', 5)

def test_gcd_exceptional_behavior_2():
    with pytest.raises(TypeError):
        gcd(5, 'b')