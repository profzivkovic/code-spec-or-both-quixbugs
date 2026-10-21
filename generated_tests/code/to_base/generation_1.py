import pytest

def test_to_base_normal_case():
    assert to_base(255, 16) == 'FF'

def test_to_base_boundary_case_low_limit():
    assert to_base(0, 2) == '0'

def test_to_base_boundary_case_high_limit():
    assert to_base(36, 37) == '10'

def test_to_base_edge_case_single_digit():
    for b in range(2, 37):
        assert to_base(b - 1, b) == str(b - 1)

def test_to_base_edge_case_zero():
    assert to_base(0, 10) == '0'

def test_to_base_exceptional_behavior_large_number():
    assert to_base(2**64, 16) == '1000000000000000'

def test_to_base_exceptional_behavior_negative_number():
    with pytest.raises(ValueError):
        to_base(-1, 10)

def test_to_base_exceptional_behavior_invalid_base_low_limit():
    with pytest.raises(ValueError):
        to_base(10, 1)

def test_to_base_exceptional_behavior_invalid_base_high_limit():
    with pytest.raises(ValueError):
        to_base(10, 37)