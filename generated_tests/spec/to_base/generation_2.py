import pytest

def test_to_base_normal_case():
    assert to_base(31, 16) == '1F'

def test_to_base_boundary_cases():
    assert to_base(0, 2) == ''
    assert to_base(1, 2) == '1'

@ pytest.mark.parametrize('num, b', [
    (35, 8),
    (64, 9),
    (77, 10),
    (88, 11),
    (99, 12),
    (110, 13),
    (121, 14),
    (132, 15),
])
def test_to_base_edge_cases(num, b):
    assert to_base(num, b) == format(num, f'0{b}x').upper()

@ pytest.mark.parametrize('num', [-1, -10, -100])
def test_to_base_exceptional_behavior_negative_input(num, b=2):
    with pytest.raises(ValueError):
        to_base(num, b)

@ pytest.mark.parametrize('b', [1, 37, 38, 'a'])
def test_to_base_exceptional_behavior_invalid_base(b, num=10):
    with pytest.raises(ValueError):
        to_base(num, b)