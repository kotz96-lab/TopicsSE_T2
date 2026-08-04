"""Tests for remove_duplicates. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import remove_duplicates as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([]) == []

def test_he_case_02():
    assert candidate([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_he_case_03():
    assert candidate([1, 2, 3, 2, 4, 3, 5]) == [1, 4, 5]

def test_extra_01():
    assert candidate([]) == []

def test_extra_02():
    assert candidate([1, 2, 3]) == [1, 2, 3]

def test_extra_03():
    assert candidate([1, 2, 3, 2, 4]) == [1, 3, 4]

def test_extra_04():
    assert candidate([1, 1, 1, 1]) == []

def test_extra_05():
    assert candidate([5, 5, 6]) == [6]

def test_extra_06():
    assert candidate([1, 2, 1, 3, 2]) == [3]

def test_extra_07():
    assert candidate([9]) == [9]
