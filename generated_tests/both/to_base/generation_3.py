import pytest

def test_to_base_normal_cases():
    assert to_base(255, 16) == 'FF'
    assert to_base(10, 2) == '1010'
    assert to_base(7, 8) == '7'
    assert to_base(31, 16) == '1F'


def test_to_base_boundary_cases():
    assert to_base(1, 2) == '1'
    assert to_base(9, 10) == '9'


def test_to_base_edge_cases():
    assert to_base(35, 36) == 'Z'


def test_to_base_exceptional_behavior():
    with pytest.raises(ValueError):
        to_base(0, 2)
    with pytest.raises(ValueError):
        to_base(10, 1)
    with pytest.raises(ValueError):
        to_base(10, 37)