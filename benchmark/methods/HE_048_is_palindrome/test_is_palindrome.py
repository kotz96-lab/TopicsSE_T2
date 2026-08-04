"""Tests for is_palindrome. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import is_palindrome as candidate  # noqa: E402


def test_he_case_01():
    assert candidate('') == True

def test_he_case_02():
    assert candidate('aba') == True

def test_he_case_03():
    assert candidate('aaaaa') == True

def test_he_case_04():
    assert candidate('zbcd') == False

def test_he_case_05():
    assert candidate('xywyx') == True

def test_he_case_06():
    assert candidate('xywyz') == False

def test_he_case_07():
    assert candidate('xywzx') == False

def test_extra_01():
    assert candidate('') == True

def test_extra_02():
    assert candidate('a') == True

def test_extra_03():
    assert candidate('ab') == False

def test_extra_04():
    assert candidate('aa') == True

def test_extra_05():
    assert candidate('racecar') == True

def test_extra_06():
    assert candidate('hello') == False

def test_extra_07():
    assert candidate('level') == True

def test_extra_08():
    assert candidate('abc') == False
