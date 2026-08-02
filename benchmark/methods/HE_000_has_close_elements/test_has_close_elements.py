"""Tests for `has_close_elements`. Imports from `buggy` by convention so the
same test file exercises the mutated version. The test runner puts the task
directory on sys.path before invoking pytest, and swaps `buggy.py` between
the mutant and the original when it needs to check that the original passes.
"""

from buggy import has_close_elements  # noqa: E402


def test_returns_false_for_empty_list():
    assert has_close_elements([], 1.0) is False


def test_returns_false_for_single_element():
    assert has_close_elements([1.0], 1.0) is False


def test_returns_false_when_all_far_apart():
    assert has_close_elements([1.0, 5.0, 10.0], 0.5) is False


def test_returns_true_for_two_close_numbers():
    assert has_close_elements([1.0, 1.1], 0.2) is True


def test_returns_true_when_middle_pair_close():
    assert has_close_elements([1.0, 2.8, 3.0, 4.0], 0.3) is True


def test_returns_false_when_threshold_equal_to_distance():
    # Original: 1.0 vs 2.0, threshold 1.0 -> distance is NOT strictly less
    # than threshold, so should be False. The buggy version uses `<=` and
    # will incorrectly return True here.
    assert has_close_elements([1.0, 2.0], 1.0) is False


def test_returns_false_for_far_apart_ints():
    assert has_close_elements([0.0, 100.0, 200.0], 1.0) is False


def test_returns_true_for_repeated_values():
    # Two elements at the same value have distance 0, which is < any positive threshold.
    assert has_close_elements([1.0, 5.0, 1.0], 0.1) is True


def test_returns_true_for_negative_numbers_close():
    assert has_close_elements([-1.0, -1.05, 3.0], 0.1) is True


def test_returns_false_for_negative_numbers_far():
    assert has_close_elements([-10.0, -5.0, 0.0, 5.0], 1.0) is False


def test_returns_true_when_first_and_last_close():
    assert has_close_elements([1.0, 10.0, 20.0, 1.05], 0.1) is True


def test_returns_false_when_threshold_very_small():
    assert has_close_elements([1.0, 1.001, 2.0], 0.0001) is False
