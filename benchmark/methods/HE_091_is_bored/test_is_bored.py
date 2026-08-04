"""Tests for is_bored. The runner puts this directory on sys.path
and swaps `buggy.py` between the mutant and the original as needed.
"""

from buggy import is_bored as candidate  # noqa: E402


def test_he_case_01():
    assert candidate("Hello world") == 0, "Test 1"

def test_he_case_02():
    assert candidate("Is the sky blue?") == 0, "Test 2"

def test_he_case_03():
    assert candidate("I love It !") == 1, "Test 3"

def test_he_case_04():
    assert candidate("bIt") == 0, "Test 4"

def test_he_case_05():
    assert candidate("I feel good today. I will be productive. will kill It") == 2, "Test 5"

def test_he_case_06():
    assert candidate("You and I are going for a walk") == 0, "Test 6"

def test_extra_01():
    assert candidate('Hello world') == 0

def test_extra_02():
    assert candidate('I am at home. I love pizza.') == 2

def test_extra_03():
    assert candidate('It is a nice day. I feel good.') == 1

def test_extra_04():
    assert candidate('Is she here? I saw her.') == 1

def test_extra_05():
    assert candidate('i am tired.') == 0

def test_extra_06():
    assert candidate('I love apples.') == 1

def test_extra_07():
    assert candidate('') == 0
