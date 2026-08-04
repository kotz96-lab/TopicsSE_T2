"""Tests for is_prime. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import is_prime as candidate  # noqa: E402


def test_he_case_01():
    assert candidate(6) == False

def test_he_case_02():
    assert candidate(101) == True

def test_he_case_03():
    assert candidate(11) == True

def test_he_case_04():
    assert candidate(13441) == True

def test_he_case_05():
    assert candidate(61) == True

def test_he_case_06():
    assert candidate(4) == False

def test_he_case_07():
    assert candidate(1) == False

def test_he_case_08():
    assert candidate(5) == True

def test_he_case_09():
    assert candidate(11) == True

def test_he_case_10():
    assert candidate(17) == True

def test_he_case_11():
    assert candidate(5 * 17) == False

def test_he_case_12():
    assert candidate(11 * 7) == False

def test_he_case_13():
    assert candidate(13441 * 19) == False

def test_extra_01():
    assert candidate(2) == True

def test_extra_02():
    assert candidate(3) == True

def test_extra_03():
    assert candidate(4) == False

def test_extra_04():
    assert candidate(5) == True

def test_extra_05():
    assert candidate(0) == False

def test_extra_06():
    assert candidate(1) == False

def test_extra_07():
    assert candidate(15) == False
