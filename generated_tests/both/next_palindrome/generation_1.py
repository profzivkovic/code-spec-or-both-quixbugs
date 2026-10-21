import pytest

def test_next_palindrome_normal_case_1():
    assert next_palindrome([1, 4, 9, 4, 1]) == [1, 5, 0, 5, 1]


def test_next_palindrome_normal_case_2():
    assert next_palindrome([9, 9, 9, 9]) == [1, 0, 0, 0, 1]


def test_next_palindrome_boundary_case_1():
    assert next_palindrome([5, 9, 9, 5]) == [6, 0, 0, 6]


def test_next_palindrome_edge_case_1():
    assert next_palindrome([1]) == [2]


def test_next_palindrome_exceptional_behavior_1():
    with pytest.raises(ValueError):
        next_palindrome([1, 3, 5, 7, 9])
