"""Tests for rescale_to_unit. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import rescale_to_unit as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([2.0, 49.9]) == [0.0, 1.0]

def test_he_case_02():
    assert candidate([100.0, 49.9]) == [1.0, 0.0]

def test_he_case_03():
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]

def test_he_case_04():
    assert candidate([2.0, 1.0, 5.0, 3.0, 4.0]) == [0.25, 0.0, 1.0, 0.5, 0.75]

def test_he_case_05():
    assert candidate([12.0, 11.0, 15.0, 13.0, 14.0]) == [0.25, 0.0, 1.0, 0.5, 0.75]

def test_extra_01():
    assert candidate([0.0, 1.0]) == [0.0, 1.0]

def test_extra_02():
    assert candidate([2.0, 6.0, 10.0]) == [0.0, 0.5, 1.0]

def test_extra_03():
    assert candidate([-1.0, 0.0, 1.0]) == [0.0, 0.5, 1.0]

def test_extra_04():
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]

def test_extra_05():
    assert candidate([10.0, 20.0]) == [0.0, 1.0]

def test_extra_06():
    assert candidate([5.0, 10.0, 15.0]) == [0.0, 0.5, 1.0]
