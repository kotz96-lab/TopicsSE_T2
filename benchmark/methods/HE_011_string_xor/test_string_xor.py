"""Tests for string_xor. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import string_xor as candidate  # noqa: E402


def test_he_case_01():
    assert candidate('111000', '101010') == '010010'

def test_he_case_02():
    assert candidate('1', '1') == '0'

def test_he_case_03():
    assert candidate('0101', '0000') == '0101'

def test_extra_01():
    assert candidate('0', '0') == '0'

def test_extra_02():
    assert candidate('1', '1') == '0'

def test_extra_03():
    assert candidate('0', '1') == '1'

def test_extra_04():
    assert candidate('1', '0') == '1'

def test_extra_05():
    assert candidate('11', '00') == '11'

def test_extra_06():
    assert candidate('101', '010') == '111'

def test_extra_07():
    assert candidate('111', '111') == '000'
