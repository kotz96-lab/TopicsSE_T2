"""End-to-end integration test: spawn pytest against the real HE_000 task
and confirm the runner + SBFL aggregator produce a sensible report.

This is slower than the unit tests (a few seconds — spawns a pytest
subprocess with coverage) but it's the only test that exercises the actual
coverage.py + pytest-cov integration.
"""

from pathlib import Path

import pytest

from src.sbfl.aggregate import build_report
from src.testing.runner import run_with_coverage


HE_000 = (
    Path(__file__).resolve().parents[1]
    / "benchmark" / "methods" / "HE_000_has_close_elements"
)


@pytest.fixture(scope="module")
def buggy_result():
    """Runs the coverage pipeline once and shares the result across tests."""
    if not HE_000.exists():
        pytest.skip("HE_000 benchmark folder not present")
    return run_with_coverage(HE_000, use_buggy=True)


class TestRunnerAgainstBuggy:
    def test_finds_the_one_expected_failing_test(self, buggy_result) -> None:
        # HE_000's mutation (< -> <=) is designed to be caught by the
        # threshold-equal-distance test. We should see exactly 1 failure.
        assert buggy_result.total_failed == 1
        assert buggy_result.total_passed >= 10
        failing_id = buggy_result.failing_tests[0]
        assert "threshold_equal_to_distance" in failing_id

    def test_captures_per_test_line_coverage(self, buggy_result) -> None:
        # Every executable line in a tiny 8-line body should have some hits.
        assert buggy_result.line_hits, "no per-test coverage captured"
        for line, tests in buggy_result.line_hits.items():
            assert tests, f"line {line} was recorded but has no test contexts"

    def test_test_ids_are_normalized_filenames(self, buggy_result) -> None:
        # After normalization there should be no path separators or |run tags.
        for outcome in buggy_result.outcomes:
            assert "/" not in outcome.test_id
            assert "\\" not in outcome.test_id
            assert "|" not in outcome.test_id
            assert outcome.test_id.startswith("test_")


class TestSbflReport:
    def test_ground_truth_line_appears_in_ranking(self, buggy_result) -> None:
        # HE_000 ground truth is line 6 (the `<=` comparison).
        report = build_report(buggy_result)
        ranked_lines = [row.line for row in report.ranking_tarantula]
        assert 6 in ranked_lines
        # A quick sanity check that top-5 usually includes it (Tarantula is
        # a heuristic; we don't require top-1 because line 7 legitimately
        # scores higher on this problem).
        assert 6 in ranked_lines[:5]

    def test_json_payload_round_trips(self, buggy_result) -> None:
        import json
        payload = build_report(buggy_result).to_json()
        rehydrated = json.loads(json.dumps(payload))
        assert rehydrated["task_id"] == "HE_000_has_close_elements"
        assert set(rehydrated["ranking"].keys()) == {"tarantula", "ochiai"}


class TestOriginalPassesAllTests:
    def test_swapping_in_original_yields_zero_failures(self) -> None:
        # Also verifies buggy.py is restored afterwards.
        if not HE_000.exists():
            pytest.skip("HE_000 benchmark folder not present")
        buggy_before = (HE_000 / "buggy.py").read_text(encoding="utf-8")
        result = run_with_coverage(HE_000, use_buggy=False)
        buggy_after = (HE_000 / "buggy.py").read_text(encoding="utf-8")
        assert result.total_failed == 0
        assert buggy_before == buggy_after
