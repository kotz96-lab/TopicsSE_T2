"""Tests for monotonic. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import monotonic as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([1, 2, 4, 10]) == True

def test_he_case_02():
    assert candidate([1, 2, 4, 20]) == True

def test_he_case_03():
    assert candidate([1, 20, 4, 10]) == False

def test_he_case_04():
    assert candidate([4, 1, 0, -10]) == True

def test_he_case_05():
    assert candidate([4, 1, 1, 0]) == True

def test_he_case_06():
    assert candidate([1, 2, 3, 2, 5, 60]) == False

def test_he_case_07():
    assert candidate([1, 2, 3, 4, 5, 60]) == True

def test_he_case_08():
    assert candidate([9, 9, 9, 9]) == True

def test_extra_01():
    assert candidate([1, 2, 4, 20]) == True

def test_extra_02():
    assert candidate([1, 20, 4, 10]) == False

def test_extra_03():
    assert candidate([4, 1, 0, -10]) == True

def test_extra_04():
    assert candidate([1, 1, 1, 1]) == True

def test_extra_05():
    assert candidate([5]) == True

def test_extra_06():
    assert candidate([3, 2, 1]) == True

def test_extra_07():
    assert candidate([1, 2, 3]) == True
