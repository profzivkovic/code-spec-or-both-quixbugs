import pytest

def test_max_sublist_sum_normal_case_1():
    assert max_sublist_sum([4, -5, 2, 1, -1, 3]) == 5

def test_max_sublist_sum_normal_case_2():
    assert max_sublist_sum([-2, -1, -6]) == -1

def test_max_sublist_sum_boundary_case_empty_list():
    assert max_sublist_sum([]) == 0

def test_max_sublist_sum_edge_case_single_element_positive():
    assert max_sublist_sum([7]) == 7

def test_max_sublist_sum_edge_case_single_element_negative():
    assert max_sublist_sum([-3]) == -3

def test_max_sublist_sum_all_negative_numbers():
    assert max_sublist_sum([-1, -2, -3, -4]) == -1

def test_max_sublist_sum_all_positive_numbers():
    assert max_sublist_sum([1, 2, 3, 4]) == 10
