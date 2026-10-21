import pytest

def test_is_valid_parenthesization_normal_case_1():
    assert is_valid_parenthesization('((()()))()') == True

def test_is_valid_parenthesization_normal_case_2():
    assert is_valid_parenthesization('()()()') == True

def test_is_valid_parenthesization_boundary_case_1():
    assert is_valid_parenthesization('()') == True

def test_is_valid_parenthesization_edge_case_1():
    assert is_valid_parenthesization('') == True

def test_is_valid_parenthesization_exceptional_behavior_case_1():
    assert is_valid_parenthesization(')()(') == False

def test_is_valid_parenthesization_exceptional_behavior_case_2():
    assert is_valid_parenthesization('(()') == False

def test_is_valid_parenthesization_exceptional_behavior_case_3():
    assert is_valid_parenthesization('())') == False