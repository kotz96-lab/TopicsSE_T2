"""Tests for greatest_common_divisor. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import greatest_common_divisor as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(3, 7) == 1

def test_he_case_02():
    assert candidate(10, 15) == 5

def test_he_case_03():
    assert candidate(49, 14) == 7

def test_he_case_04():
    assert candidate(144, 60) == 12

def test_extra_01():
    assert candidate(12, 18) == 6

def test_extra_02():
    assert candidate(100, 25) == 25

def test_extra_03():
    assert candidate(7, 13) == 1

def test_extra_04():
    assert candidate(48, 60) == 12

def test_extra_05():
    assert candidate(9, 3) == 3

def test_extra_06():
    assert candidate(1, 1) == 1

def test_extra_07():
    assert candidate(50, 15) == 5
