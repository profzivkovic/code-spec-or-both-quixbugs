def test_quicksort_empty_list(quicksort):
    assert quicksort([]) == [], 'Empty list should return an empty list'


def test_quicksort_single_element(quicksort):
    assert quicksort([1]) == [1], 'Single element list should return the same list'


def test_quicksort_sorted_list(quicksort):
    assert quicksort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], 'Sorted list should remain sorted'


def test_quicksort_reverse_sorted_list(quicksort):
    assert quicksort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], 'Reverse sorted list should be sorted'


def test_quicksort_random_list(quicksort):
    assert quicksort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10], 'Random list should be sorted'


def test_quicksort_with_duplicates(quicksort):
    assert quicksort([5, 3, 5, 2, 3, 3, 9, 0, 123]) == [0, 2, 3, 3, 3, 5, 5, 9, 123], 'List with duplicates should be sorted'


def test_quicksort_with_negative_numbers(quicksort):
    assert quicksort([-3, -6, -8, -10, -1]) == [-10, -8, -6, -3, -1], 'List with negative numbers should be sorted'
