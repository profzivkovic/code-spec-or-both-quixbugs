import pytest

def test_max_sublist_sum_normal_case_1():
    assert max_sublist_sum([4, -5, 2, 1, -1, 3]) == 5

def test_max_sublist_sum_normal_case_2():
    assert max_sublist_sum([-2, -1, -3]) == -1

def test_max_sublist_sum_single_element_positive():
    assert max_sublist_sum([7]) == 7

def test_max_sublist_sum_single_element_negative():
    assert max_sublist_sum([-5]) == -5

def test_max_sublist_sum_all_zeros():
    assert max_sublist_sum([0, 0, 0]) == 0

def test_max_sublist_sum_empty_list():
    assert max_sublist_sum([]) == 0
