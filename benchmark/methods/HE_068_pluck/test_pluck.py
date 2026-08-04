"""Tests for pluck. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import pluck as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([4,2,3]) == [2, 1], "Error"

def test_he_case_02():
    assert candidate([1,2,3]) == [2, 1], "Error"

def test_he_case_03():
    assert candidate([]) == [], "Error"

def test_he_case_04():
    assert candidate([5, 0, 3, 0, 4, 2]) == [0, 1], "Error"

def test_he_case_05():
    assert candidate([1, 2, 3, 0, 5, 3]) == [0, 3], "Error"

def test_he_case_06():
    assert candidate([5, 4, 8, 4 ,8]) == [4, 1], "Error"

def test_he_case_07():
    assert candidate([7, 6, 7, 1]) == [6, 1], "Error"

def test_he_case_08():
    assert candidate([7, 9, 7, 1]) == [], "Error"

def test_extra_01():
    assert candidate([]) == []

def test_extra_02():
    assert candidate([4, 2, 3]) == [2, 1]

def test_extra_03():
    assert candidate([1, 2, 3]) == [2, 1]

def test_extra_04():
    assert candidate([5, 0, 3, 0, 4, 2]) == [0, 1]

def test_extra_05():
    assert candidate([1, 3, 5]) == []

def test_extra_06():
    assert candidate([2, 4, 6]) == [2, 0]

def test_extra_07():
    assert candidate([1, 2, 4]) == [2, 1]
