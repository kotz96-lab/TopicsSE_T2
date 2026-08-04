"""Tests for longest. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import longest as candidate  # noqa: E402


def test_he_case_01():
    assert candidate([]) == None

def test_he_case_02():
    assert candidate(['x', 'y', 'z']) == 'x'

def test_he_case_03():
    assert candidate(['x', 'yyy', 'zzzz', 'www', 'kkkk', 'abc']) == 'zzzz'

def test_extra_01():
    assert candidate([]) is None

def test_extra_02():
    assert candidate(['a']) == 'a'

def test_extra_03():
    assert candidate(['a', 'bb', 'ccc']) == 'ccc'

def test_extra_04():
    assert candidate(['aaa', 'bb', 'c']) == 'aaa'

def test_extra_05():
    assert candidate(['hi', 'hello', 'hey']) == 'hello'

def test_extra_06():
    assert candidate(['same', 'size']) == 'same'

def test_extra_07():
    assert candidate(['x', 'yy', 'zzz', 'wwww']) == 'wwww'
