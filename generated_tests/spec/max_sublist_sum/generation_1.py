import pytest

def test_max_sublist_sum_positive_numbers():
    assert max_sublist_sum([4, -5, 2, 1, -1, 3]) == 5

def test_max_sublist_sum_all_negative_numbers():
    assert max_sublist_sum([-1, -2, -3, -4, -5]) == -1

def test_max_sublist_sum_single_positive_number():
    assert max_sublist_sum([7]) == 7

def test_max_sublist_sum_single_negative_number():
    assert max_sublist_sum([-3]) == -3

def test_max_sublist_sum_empty_list():
    assert max_sublist_sum([]) == 0

def test_max_sublist_sum_all_zeros():
    assert max_sublist_sum([0, 0, 0, 0]) == 0

def test_max_sublist_sum_with_zero_in_middle():
    assert max_sublist_sum([1, -2, 3, -4, 5]) == 9