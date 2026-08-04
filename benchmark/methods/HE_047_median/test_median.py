"""Tests for median. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import median as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([3, 1, 2, 4, 5]) == 3

def test_he_case_02():
    assert candidate([-10, 4, 6, 1000, 10, 20]) == 8.0

def test_he_case_03():
    assert candidate([5]) == 5

def test_he_case_04():
    assert candidate([6, 5]) == 5.5

def test_he_case_05():
    assert candidate([8, 1, 3, 9, 9, 2, 7]) == 7

def test_extra_01():
    assert candidate([3, 1, 2]) == 2

def test_extra_02():
    assert candidate([1, 2, 3, 4]) == 2.5

def test_extra_03():
    assert candidate([5]) == 5

def test_extra_04():
    assert candidate([1, 2]) == 1.5

def test_extra_05():
    assert candidate([-10, 4, 6, 1000, 10, 20]) == 8.0

def test_extra_06():
    assert candidate([7, 3, 1, 5]) == 4.0

def test_extra_07():
    assert candidate([0, 0, 0, 1]) == 0.0
