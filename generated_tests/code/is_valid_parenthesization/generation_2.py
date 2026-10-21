import pytest

def test_is_valid_parenthesization_normal_cases(function):
    assert function('()') == True
    assert function('(()())') == True
    assert function('(())') == True


def test_is_valid_parenthesization_boundary_cases(function):
    assert function('') == True
    assert function('(') == False
    assert function(')') == False


def test_is_valid_parenthesization_edge_cases(function):
    assert function('((()))') == True
    assert function('(()') == False
    assert function('())') == False


def test_is_valid_parenthesization_exceptional_behavior(function):
    assert function(None) is None