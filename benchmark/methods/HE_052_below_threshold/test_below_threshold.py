"""Tests for below_threshold. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import below_threshold as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([1, 2, 4, 10], 100)

def test_he_case_02():
    assert not candidate([1, 20, 4, 10], 5)

def test_he_case_03():
    assert candidate([1, 20, 4, 10], 21)

def test_he_case_04():
    assert candidate([1, 20, 4, 10], 22)

def test_he_case_05():
    assert candidate([1, 8, 4, 10], 11)

def test_he_case_06():
    assert not candidate([1, 8, 4, 10], 10)

def test_extra_01():
    assert candidate([], 100) == True

def test_extra_02():
    assert candidate([5, 5, 5], 5) == False

def test_extra_03():
    assert candidate([1, 2, 3], 3) == False

def test_extra_04():
    assert candidate([1, 2, 3], 4) == True

def test_extra_05():
    assert candidate([10], 10) == False

def test_extra_06():
    assert candidate([-1, -2, -3], 0) == True
