import pytest

def test_next_palindrome_normal_case_1():
    assert next_palindrome([1, 4, 9, 4, 1]) == [1, 5, 0, 5, 1]


def test_next_palindrome_normal_case_2():
    assert next_palindrome([9, 9, 9]) == [1, 0, 0, 1]


def test_next_palindrome_boundary_case_odd_length():
    assert next_palindrome([8, 7, 6, 5, 4, 3, 2, 1]) == [8, 7, 6, 6, 6, 6, 7, 8]


def test_next_palindrome_boundary_case_even_length():
    assert next_palindrome([8, 7, 6, 5, 4, 3, 2]) == [8, 7, 6, 6, 6, 7, 8]


def test_next_palindrome_edge_case_single_digit_9():
    assert next_palindrome([9]) == [1, 0, 1]


def test_next_palindrome_edge_case_single_digit_0():
    assert next_palindrome([0]) == [1]


def test_next_palindrome_edge_case_all_nines():
    assert next_palindrome([9, 9, 9, 9]) == [1, 0, 0, 0, 0, 1]
