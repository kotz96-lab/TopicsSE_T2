"""Tests for max_element. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import max_element as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([1, 2, 3]) == 3

def test_he_case_02():
    assert candidate([5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10]) == 124

def test_extra_01():
    assert candidate([1, 2, 3]) == 3

def test_extra_02():
    assert candidate([3, 2, 1]) == 3

def test_extra_03():
    assert candidate([-1, -2, -3]) == -1

def test_extra_04():
    assert candidate([5]) == 5

def test_extra_05():
    assert candidate([1, 100, 50, 200, 3]) == 200

def test_extra_06():
    assert candidate([0, 0, 0]) == 0

def test_extra_07():
    assert candidate([-100, 0, 100]) == 100

def test_extra_08():
    assert candidate([7, 7, 8]) == 8
