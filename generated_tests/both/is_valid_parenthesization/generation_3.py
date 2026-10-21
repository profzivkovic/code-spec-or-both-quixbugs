import pytest

def test_is_valid_parenthesization_normal_cases():
    assert is_valid_parenthesization('((()()))()') == True
    assert is_valid_parenthesization('()()()') == True
    assert is_valid_parenthesization('(()())') == True

def test_is_valid_parenthesization_boundary_cases():
    assert is_valid_parenthesization('') == True
    assert is_valid_parenthesization('()') == True
    assert is_valid_parenthesization('((()))') == True

def test_is_valid_parenthesization_edge_cases():
    assert is_valid_parenthesization('(()') == False
    assert is_valid_parenthesization('())') == False
    assert is_valid_parenthesization(')(') == False

def test_is_valid_parenthesization_exceptional_behavior():
    with pytest.raises(TypeError):
        is_valid_parenthesization('((()()))(123)')
