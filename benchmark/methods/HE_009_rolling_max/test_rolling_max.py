"""Tests for rolling_max. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import rolling_max as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([]) == []

def test_he_case_02():
    assert candidate([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_he_case_03():
    assert candidate([4, 3, 2, 1]) == [4, 4, 4, 4]

def test_he_case_04():
    assert candidate([3, 2, 3, 100, 3]) == [3, 3, 3, 100, 100]

def test_extra_01():
    assert candidate([]) == []

def test_extra_02():
    assert candidate([1, 2, 3, 2, 3, 4, 2]) == [1, 2, 3, 3, 3, 4, 4]

def test_extra_03():
    assert candidate([5, 4, 3, 2, 1]) == [5, 5, 5, 5, 5]

def test_extra_04():
    assert candidate([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

def test_extra_05():
    assert candidate([3, 3, 3]) == [3, 3, 3]

def test_extra_06():
    assert candidate([-1, -2, 0, -3]) == [-1, -1, 0, 0]

def test_extra_07():
    assert candidate([7]) == [7]
