"""Tests for sort_third. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import sort_third as candidate  # noqa: E402


def test_he_case_01():
    assert tuple(candidate([5, 6, 3, 4, 8, 9, 2])) == tuple([2, 6, 3, 4, 8, 9, 5])

def test_he_case_02():
    assert tuple(candidate([5, 8, 3, 4, 6, 9, 2])) == tuple([2, 8, 3, 4, 6, 9, 5])

def test_he_case_03():
    assert tuple(candidate([5, 6, 9, 4, 8, 3, 2])) == tuple([2, 6, 9, 4, 8, 3, 5])

def test_he_case_04():
    assert tuple(candidate([5, 6, 3, 4, 8, 9, 2, 1])) == tuple([2, 6, 3, 4, 8, 9, 5, 1])

def test_extra_01():
    assert candidate([1, 2, 3]) == [1, 2, 3]

def test_extra_02():
    assert candidate([5, 6, 3, 4, 8, 9, 2]) == [2, 6, 3, 4, 8, 9, 5]

def test_extra_03():
    assert candidate([]) == []

def test_extra_04():
    assert candidate([1]) == [1]

def test_extra_05():
    assert candidate([10, 20, 30, 40, 50, 60, 70]) == [10, 20, 30, 40, 50, 60, 70]

def test_extra_06():
    assert candidate([9, 1, 2, 6, 4, 5, 3]) == [3, 1, 2, 6, 4, 5, 9]

def test_extra_07():
    assert candidate([1, 2, 4, 3]) == [1, 2, 4, 3]

def test_extra_08():
    assert candidate([7, 8, 9]) == [7, 8, 9]

def test_extra_09():
    assert candidate([2, 1]) == [2, 1]

def test_extra_10():
    assert candidate([3, 2, 1]) == [3, 2, 1]
