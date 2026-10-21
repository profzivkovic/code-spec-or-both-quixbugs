import pytest

def test_to_base_normal_cases():
    assert to_base(10, 2) == 'A'
    assert to_base(255, 16) == 'FF'
    assert to_base(100, 3) == '10201'

def test_to_base_boundary_cases():
    assert to_base(0, 2) == ''
    assert to_base(1, 2) == '1'

def test_to_base_edge_cases():
    with pytest.raises(ValueError):
        to_base(-1, 2)

def test_to_base_exceptional_behavior():
    with pytest.raises(TypeError):
        to_base('10', 2)