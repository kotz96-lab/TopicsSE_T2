"""Tests for fib. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import fib as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(10) == 55

def test_he_case_02():
    assert candidate(1) == 1

def test_he_case_03():
    assert candidate(8) == 21

def test_he_case_04():
    assert candidate(11) == 89

def test_he_case_05():
    assert candidate(12) == 144

def test_extra_01():
    assert candidate(0) == 0

def test_extra_02():
    assert candidate(1) == 1

def test_extra_03():
    assert candidate(2) == 1

def test_extra_04():
    assert candidate(3) == 2

def test_extra_05():
    assert candidate(4) == 3

def test_extra_06():
    assert candidate(5) == 5

def test_extra_07():
    assert candidate(6) == 8

def test_extra_08():
    assert candidate(7) == 13
