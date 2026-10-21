import pytest

def test_gcd_normal_case():
    assert gcd(48, 18) == 6

@pytest.mark.parametrize('a,b,expected', [
    (0, 5, 5),
    (5, 0, 5),
    (-3, 9, 3),
    (-9, -3, 3)
])
def test_gcd_boundary_and_edge_cases(a, b, expected):
    assert gcd(a, b) == expected

@pytest.mark.parametrize('a,b', [
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, -1)
])
def test_gcd_exceptional_behavior(a, b):
    with pytest.raises(ZeroDivisionError):
        gcd(a, b)