import pytest

def test_next_palindrome_normal_case():
    assert next_palindrome([1, 2, 3, 2, 1]) == [1, 3, 4, 3, 1]

def test_next_palindrome_boundary_case_odd_length():
    assert next_palindrome([9, 8, 7, 8, 9]) == [9, 9, 0, 9, 9]

def test_next_palindrome_boundary_case_even_length():
    assert next_palindrome([9, 8, 7, 6, 5, 4, 3, 2, 1]) == [9, 9, 0, 0, 0, 0, 0, 9, 9]

def test_next_palindrome_edge_case_all_nines_odd_length():
    assert next_palindrome([9, 9, 9]) == [1, 0, 0, 0, 1]

def test_next_palindrome_edge_case_all_nines_even_length():
    assert next_palindrome([9, 9, 9, 9]) == [1, 0, 0, 0, 0, 1]

if __name__ == '__main__':
    pytest.main()