"""Tests for vowels_count. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import vowels_count as candidate  # noqa: E402


def test_he_case_01():
    assert candidate("abcde") == 2, "Test 1"

def test_he_case_02():
    assert candidate("Alone") == 3, "Test 2"

def test_he_case_03():
    assert candidate("key") == 2, "Test 3"

def test_he_case_04():
    assert candidate("bye") == 1, "Test 4"

def test_he_case_05():
    assert candidate("keY") == 2, "Test 5"

def test_he_case_06():
    assert candidate("bYe") == 1, "Test 6"

def test_he_case_07():
    assert candidate("ACEDY") == 3, "Test 7"

def test_extra_01():
    assert candidate('hello') == 2

def test_extra_02():
    assert candidate('sky') == 1

def test_extra_03():
    assert candidate('WHY') == 1

def test_extra_04():
    assert candidate('a') == 1

def test_extra_05():
    assert candidate('b') == 0

def test_extra_06():
    assert candidate('bcd') == 0

def test_extra_07():
    assert candidate('happy') == 2

def test_extra_08():
    assert candidate('AEIOU') == 5
