"""Tests for triangle_area. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import triangle_area as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(3, 4, 5) == 6.00, "This prints if this assert fails 1 (good for debugging!)"

def test_he_case_02():
    assert candidate(1, 2, 10) == -1

def test_he_case_03():
    assert candidate(4, 8, 5) == 8.18

def test_he_case_04():
    assert candidate(2, 2, 2) == 1.73

def test_he_case_05():
    assert candidate(1, 2, 3) == -1

def test_he_case_06():
    assert candidate(10, 5, 7) == 16.25

def test_he_case_07():
    assert candidate(2, 6, 3) == -1

def test_he_case_08():
    assert candidate(1, 1, 1) == 0.43, "This prints if this assert fails 2 (also good for debugging!)"

def test_he_case_09():
    assert candidate(2, 2, 10) == -1

def test_extra_01():
    assert candidate(3, 4, 5) == 6.0

def test_extra_02():
    assert candidate(1, 2, 3) == -1

def test_extra_03():
    assert candidate(2, 2, 4) == -1

def test_extra_04():
    assert candidate(1, 2, 10) == -1

def test_extra_05():
    assert candidate(6, 8, 10) == 24.0

def test_extra_06():
    assert candidate(3, 3, 3) == round(3.897114317029974, 2)
