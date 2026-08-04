"""Tests for fibfib. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import fibfib as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(2) == 1

def test_he_case_02():
    assert candidate(1) == 0

def test_he_case_03():
    assert candidate(5) == 4

def test_he_case_04():
    assert candidate(8) == 24

def test_he_case_05():
    assert candidate(10) == 81

def test_he_case_06():
    assert candidate(12) == 274

def test_he_case_07():
    assert candidate(14) == 927

def test_extra_01():
    assert candidate(0) == 0

def test_extra_02():
    assert candidate(1) == 0

def test_extra_03():
    assert candidate(2) == 1

def test_extra_04():
    assert candidate(3) == 1

def test_extra_05():
    assert candidate(4) == 2

def test_extra_06():
    assert candidate(5) == 4

def test_extra_07():
    assert candidate(6) == 7

def test_extra_08():
    assert candidate(7) == 13
