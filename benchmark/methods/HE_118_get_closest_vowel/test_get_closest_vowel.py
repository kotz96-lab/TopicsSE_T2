"""Tests for get_closest_vowel. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import get_closest_vowel as candidate  # noqa: E402


def test_he_case_01():
    assert candidate("yogurt") == "u"

def test_he_case_02():
    assert candidate("full") == "u"

def test_he_case_03():
    assert candidate("easy") == ""

def test_he_case_04():
    assert candidate("eAsy") == ""

def test_he_case_05():
    assert candidate("ali") == ""

def test_he_case_06():
    assert candidate("bad") == "a"

def test_he_case_07():
    assert candidate("most") == "o"

def test_he_case_08():
    assert candidate("ab") == ""

def test_he_case_09():
    assert candidate("ba") == ""

def test_he_case_10():
    assert candidate("quick") == ""

def test_he_case_11():
    assert candidate("anime") == "i"

def test_he_case_12():
    assert candidate("Asia") == ""

def test_he_case_13():
    assert candidate("Above") == "o"

def test_extra_01():
    assert candidate('yogurt') == 'u'

def test_extra_02():
    assert candidate('FULL') == 'U'

def test_extra_03():
    assert candidate('quick') == ''

def test_extra_04():
    assert candidate('ab') == ''

def test_extra_05():
    assert candidate('') == ''

def test_extra_06():
    assert candidate('easy') == ''

def test_extra_07():
    assert candidate('Iain') == ''
