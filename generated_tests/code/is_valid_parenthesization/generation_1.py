import pytest

def test_is_valid_parenthesization():
    assert is_valid_parenthesization('()') == True
    assert is_valid_parenthesization('(()())') == True
    assert is_valid_parenthesization('((()))') == True
    assert is_valid_parenthesization(')(') == False
    assert is_valid_parenthesization('(((((((') == False
    assert is_valid_parenthesization(')))))))') == False
    assert is_valid_parenthesization('(()')) == False
    assert is_valid_parenthesization('())') == False
    assert is_valid_parenthesization('()()') == True
    assert is_valid_parenthesization('') == True
