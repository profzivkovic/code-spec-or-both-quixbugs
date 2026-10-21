import pytest

def test_to_base_normal_case():
    assert to_base(255, 16) == 'FF'

def test_to_base_boundary_case_low_limit():
    assert to_base(35, 36) == 'Z'

def test_to_base_boundary_case_high_limit():
    assert to_base(2, 2) == '10'

def test_to_base_edge_case_single_digit():
    assert to_base(7, 8) == '7'

def test_to_base_exceptional_behavior_zero_input():
    with pytest.raises(ValueError):
        to_base(0, 10)

def test_to_base_exceptional_behavior_negative_number():
    with pytest.raises(ValueError):
        to_base(-1, 10)

def test_to_base_exceptional_behavior_invalid_base_low_limit():
    with pytest.raises(ValueError):
        to_base(10, 1)

def test_to_base_exceptional_behavior_invalid_base_high_limit():
    with pytest.raises(ValueError):
        to_base(10, 37)