import pytest

def test_to_base_normal_case_1():
    assert to_base(31, 16) == '1F'

def test_to_base_normal_case_2():
    assert to_base(255, 8) == '377'

def test_to_base_boundary_case_1():
    assert to_base(9, 10) == '9'

def test_to_base_boundary_case_2():
    assert to_base(16, 16) == '10'

def test_to_base_edge_case_1():
    assert to_base(1, 36) == '1'

def test_to_base_edge_case_2():
    assert to_base(35, 36) == 'Z'

def test_to_base_exceptional_behavior_1():
    with pytest.raises(ValueError):
        to_base(-1, 10)

def test_to_base_exceptional_behavior_2():
    with pytest.raises(ValueError):
        to_base(10, 1)

def test_to_base_exceptional_behavior_3():
    with pytest.raises(ValueError):
        to_base(10, 37)
