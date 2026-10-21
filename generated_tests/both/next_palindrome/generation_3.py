import pytest

def test_next_palindrome_normal_case():
    assert next_palindrome([1, 4, 9, 4, 1]) == [1, 5, 0, 5, 1]

def test_next_palindrome_boundary_case_even_length():
    assert next_palindrome([9, 9, 9]) == [1, 0, 0, 0, 1]

def test_next_palindrome_boundary_case_odd_length():
    assert next_palindrome([9, 9, 9, 9]) == [1, 0, 0, 0, 0, 1]

def test_next_palindrome_edge_case_single_digit():
    assert next_palindrome([9]) == [1, 0, 1]

def test_next_palindrome_edge_case_all_nines_even_length():
    assert next_palindrome([9, 9]) == [1, 0, 1]

def test_next_palindrome_edge_case_all_nines_odd_length():
    assert next_palindrome([9, 9, 9]) == [1, 0, 0, 0, 1]
