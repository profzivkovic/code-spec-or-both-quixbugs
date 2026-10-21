def test_next_palindrome_normal_case():
    assert next_palindrome([1, 4, 9, 4, 1]) == [1, 5, 0, 5, 1]

def test_next_palindrome_boundary_case():
    assert next_palindrome([9, 9, 9]) == [1, 0, 0, 1]

def test_next_palindrome_edge_case_single_digit():
    assert next_palindrome([3]) == [4]

def test_next_palindrome_odd_length_palindrome():
    assert next_palindrome([2, 3, 5, 3, 2]) == [2, 3, 6, 3, 2]

def test_next_palindrome_even_length_palindrome_with_carry_over():
    assert next_palindrome([9, 9]) == [1, 0, 1]
