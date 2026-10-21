import pytest

def test_max_sublist_sum_normal_case():
    assert max_sublist_sum([1, -2, 3, 4]) == 7


def test_max_sublist_sum_all_negative():
    assert max_sublist_sum([-1, -2, -3, -4]) == 0


def test_max_sublist_sum_empty_list():
    assert max_sublist_sum([]) == 0


def test_max_sublist_sum_single_element():
    assert max_sublist_sum([5]) == 5


def test_max_sublist_sum_with_zeroes():
    assert max_sublist_sum([1, -2, 3, 4, 0, -1]) == 7
