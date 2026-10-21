import pytest

def test_to_base_normal_case():
    assert to_base(10, 2) == 'A'

def test_to_base_boundary_case():
    assert to_base(9, 8) == '11'

def test_to_base_edge_case_lowest_base():
    with pytest.raises(ValueError):
        to_base(5, 1)

def test_to_base_edge_case_highest_base():
    assert to_base(26, 36) == '1A'

def test_to_base_zero_input():
    assert to_base(0, 10) == ''

