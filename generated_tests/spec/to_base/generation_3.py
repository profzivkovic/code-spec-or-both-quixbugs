import pytest

def test_to_base_normal_cases():
    assert to_base(31, 16) == '1F'
    assert to_base(255, 8) == '377'
    assert to_base(100, 2) == '1100100'

def test_to_base_boundary_cases():
    assert to_base(1, 16) == '1'
    assert to_base(35, 36) == 'Z'

def test_to_base_edge_cases():
    assert to_base(99, 2) == '1100011'
    assert to_base(42, 3) == '11110'

def test_to_base_exceptional_behavior():
    with pytest.raises(ValueError):
        to_base(-1, 16)
    with pytest.raises(ValueError):
        to_base(31, 1)
    with pytest.raises(ValueError):
        to_base(31, 37)