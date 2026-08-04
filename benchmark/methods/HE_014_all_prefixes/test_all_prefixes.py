"""Tests for all_prefixes. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import all_prefixes as candidate  # noqa: E402


def test_he_case_01():
    assert candidate('') == []

def test_he_case_02():
    assert candidate('asdfgh') == ['a', 'as', 'asd', 'asdf', 'asdfg', 'asdfgh']

def test_he_case_03():
    assert candidate('WWW') == ['W', 'WW', 'WWW']

def test_extra_01():
    assert candidate('') == []

def test_extra_02():
    assert candidate('a') == ['a']

def test_extra_03():
    assert candidate('ab') == ['a', 'ab']

def test_extra_04():
    assert candidate('abc') == ['a', 'ab', 'abc']

def test_extra_05():
    assert candidate('xyz') == ['x', 'xy', 'xyz']

def test_extra_06():
    assert candidate('hello') == ['h', 'he', 'hel', 'hell', 'hello']

def test_extra_07():
    assert candidate('1234') == ['1', '12', '123', '1234']
