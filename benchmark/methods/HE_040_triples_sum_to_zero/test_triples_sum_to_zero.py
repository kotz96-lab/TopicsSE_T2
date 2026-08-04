"""Tests for triples_sum_to_zero. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import triples_sum_to_zero as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([1, 3, 5, 0]) == False

def test_he_case_02():
    assert candidate([1, 3, 5, -1]) == False

def test_he_case_03():
    assert candidate([1, 3, -2, 1]) == True

def test_he_case_04():
    assert candidate([1, 2, 3, 7]) == False

def test_he_case_05():
    assert candidate([1, 2, 5, 7]) == False

def test_he_case_06():
    assert candidate([2, 4, -5, 3, 9, 7]) == True

def test_he_case_07():
    assert candidate([1]) == False

def test_he_case_08():
    assert candidate([1, 3, 5, -100]) == False

def test_he_case_09():
    assert candidate([100, 3, 5, -100]) == False

def test_extra_01():
    assert candidate([1, 3, 5, 0]) == False

def test_extra_02():
    assert candidate([1, 3, 5, -8]) == True

def test_extra_03():
    assert candidate([1, 3, -2, 1]) == True

def test_extra_04():
    assert candidate([0, 0, 0]) == True

def test_extra_05():
    assert candidate([1, 2, 3, 4]) == False

def test_extra_06():
    assert candidate([1, 2, -3]) == True

def test_extra_07():
    assert candidate([2, 4, 6]) == False
