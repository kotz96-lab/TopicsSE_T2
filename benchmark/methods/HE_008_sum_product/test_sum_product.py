"""Tests for sum_product. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import sum_product as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([]) == (0, 1)

def test_he_case_02():
    assert candidate([1, 1, 1]) == (3, 1)

def test_he_case_03():
    assert candidate([100, 0]) == (100, 0)

def test_he_case_04():
    assert candidate([3, 5, 7]) == (3 + 5 + 7, 3 * 5 * 7)

def test_he_case_05():
    assert candidate([10]) == (10, 10)

def test_extra_01():
    assert candidate([]) == (0, 1)

def test_extra_02():
    assert candidate([1, 2, 3, 4]) == (10, 24)

def test_extra_03():
    assert candidate([0, 1, 2]) == (3, 0)

def test_extra_04():
    assert candidate([5]) == (5, 5)

def test_extra_05():
    assert candidate([-1, 1]) == (0, -1)

def test_extra_06():
    assert candidate([2, 2, 2]) == (6, 8)

def test_extra_07():
    assert candidate([10, 20]) == (30, 200)
