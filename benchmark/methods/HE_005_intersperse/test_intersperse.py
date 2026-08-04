"""Tests for intersperse. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import intersperse as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([], 7) == []

def test_he_case_02():
    assert candidate([5, 6, 3, 2], 8) == [5, 8, 6, 8, 3, 8, 2]

def test_he_case_03():
    assert candidate([2, 2, 2], 2) == [2, 2, 2, 2, 2]

def test_extra_01():
    assert candidate([], 4) == []

def test_extra_02():
    assert candidate([1], 4) == [1]

def test_extra_03():
    assert candidate([1, 2], 4) == [1, 4, 2]

def test_extra_04():
    assert candidate([1, 2, 3], 0) == [1, 0, 2, 0, 3]

def test_extra_05():
    assert candidate([5, 6, 7, 8], 9) == [5, 9, 6, 9, 7, 9, 8]

def test_extra_06():
    assert candidate([1, 1], 0) == [1, 0, 1]

def test_extra_07():
    assert candidate([-1, 0, 1], 100) == [-1, 100, 0, 100, 1]
