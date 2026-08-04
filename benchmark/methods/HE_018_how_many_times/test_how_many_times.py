"""Tests for how_many_times. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import how_many_times as candidate  # noqa: E402


def test_he_case_01():
    assert candidate('', 'x') == 0

def test_he_case_02():
    assert candidate('xyxyxyx', 'x') == 4

def test_he_case_03():
    assert candidate('cacacacac', 'cac') == 4

def test_he_case_04():
    assert candidate('john doe', 'john') == 1

def test_extra_01():
    assert candidate('', 'a') == 0

def test_extra_02():
    assert candidate('a', 'a') == 1

def test_extra_03():
    assert candidate('aa', 'a') == 2

def test_extra_04():
    assert candidate('abcabc', 'abc') == 2

def test_extra_05():
    assert candidate('aaaa', 'aa') == 3

def test_extra_06():
    assert candidate('abc', 'd') == 0

def test_extra_07():
    assert candidate('xxyz', 'z') == 1
