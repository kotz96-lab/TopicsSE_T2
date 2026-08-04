"""Tests for below_zero. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import below_zero as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([]) == False

def test_he_case_02():
    assert candidate([1, 2, -3, 1, 2, -3]) == False

def test_he_case_03():
    assert candidate([1, 2, -4, 5, 6]) == True

def test_he_case_04():
    assert candidate([1, -1, 2, -2, 5, -5, 4, -4]) == False

def test_he_case_05():
    assert candidate([1, -1, 2, -2, 5, -5, 4, -5]) == True

def test_he_case_06():
    assert candidate([1, -2, 2, -2, 5, -5, 4, -4]) == True

def test_extra_01():
    assert candidate([]) == False

def test_extra_02():
    assert candidate([1, -1]) == False

def test_extra_03():
    assert candidate([0]) == False

def test_extra_04():
    assert candidate([5]) == False

def test_extra_05():
    assert candidate([-1]) == True

def test_extra_06():
    assert candidate([1, 2, 3, -5]) == False

def test_extra_07():
    assert candidate([1, 2, 3, -7]) == True
