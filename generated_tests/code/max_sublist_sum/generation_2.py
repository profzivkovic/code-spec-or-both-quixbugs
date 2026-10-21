import pytest

def test_max_sublist_sum_positive_numbers():
    assert max_sublist_sum([1, 2, 3]) == 6
    assert max_sublist_sum([4, -1, 2, 1]) == 6


def test_max_sublist_sum_negative_numbers():
    assert max_sublist_sum([-1, -2, -3]) == 0
    assert max_sublist_sum([-2, -1, -5, -4]) == 0


def test_max_sublist_sum_mixed_numbers():
    assert max_sublist_sum([1, -2, 3, -4, 5, -6]) == 5


def test_max_sublist_sum_empty_list():
    assert max_sublist_sum([]) == 0


def test_max_sublist_sum_single_element_positive():
    assert max_sublist_sum([10]) == 10


def test_max_sublist_sum_single_element_negative():
    assert max_sublist_sum([-10]) == 0
