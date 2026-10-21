import pytest

def test_max_sublist_sum_positive_numbers():
    assert max_sublist_sum([1, 2, 3, 4]) == 10

def test_max_sublist_sum_negative_numbers():
    assert max_sublist_sum([-1, -2, -3, -4]) == 0

def test_max_sublist_sum_mixed_numbers():
    assert max_sublist_sum([-1, 2, -3, 4, -5]) == 4

def test_max_sublist_sum_single_element_positive():
    assert max_sublist_sum([7]) == 7

def test_max_sublist_sum_single_element_negative():
    assert max_sublist_sum([-7]) == 0

def test_max_sublist_sum_empty_list():
    assert max_sublist_sum([]) == 0