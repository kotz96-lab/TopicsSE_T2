"""Tests for fib4. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import fib4 as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(5) == 4

def test_he_case_02():
    assert candidate(8) == 28

def test_he_case_03():
    assert candidate(10) == 104

def test_he_case_04():
    assert candidate(12) == 386

def test_extra_01():
    assert candidate(0) == 0

def test_extra_02():
    assert candidate(1) == 0

def test_extra_03():
    assert candidate(2) == 2

def test_extra_04():
    assert candidate(3) == 0

def test_extra_05():
    assert candidate(4) == 2

def test_extra_06():
    assert candidate(5) == 4

def test_extra_07():
    assert candidate(6) == 8

def test_extra_08():
    assert candidate(7) == 14
