import pytest

def test_to_base_normal_cases():
    assert to_base(10, 2) == '1010'
    assert to_base(31, 16) == '1F'
    assert to_base(255, 8) == '377'


def test_to_base_boundary_cases():
    assert to_base(1, 2) == '1'
    assert to_base(36, 36) == 'Z'


def test_to_base_edge_cases():
    with pytest.raises(ValueError):
        to_base(-10, 2)
    with pytest.raises(ValueError):
        to_base(10, 1)
    with pytest.raises(ValueError):
        to_base(10, 37)


def test_to_base_exceptional_behavior():
    assert to_base(0, 10) == ''
