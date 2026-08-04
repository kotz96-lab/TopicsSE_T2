"""Tests for building SBFL spectra/reports from an ExecutionResult."""

from src.sbfl.aggregate import build_report, build_spectra
from src.testing.runner import ExecutionResult, TestOutcome


def _mk_result(
    *,
    outcomes: list[tuple[str, bool]],
    line_hits: dict[int, set[str]],
    task_id: str = "task",
) -> ExecutionResult:
    return ExecutionResult(
        task_id=task_id,
        outcomes=[TestOutcome(test_id=t, passed=p) for t, p in outcomes],
        line_hits=line_hits,
    )


class TestBuildSpectra:
    def test_counts_pass_and_fail_hits_per_line(self) -> None:
        result = _mk_result(
            outcomes=[("t1", True), ("t2", True), ("t3", False)],
            line_hits={
                1: {"t1", "t2", "t3"},   # 2 pass, 1 fail
                2: {"t3"},                # 0 pass, 1 fail
                3: {"t1"},                # 1 pass, 0 fail
            },
        )
        spectra = build_spectra(result)
        by_line = {s.line: s for s in spectra}
        assert by_line[1].passed == 2 and by_line[1].failed == 1
        assert by_line[2].passed == 0 and by_line[2].failed == 1
        assert by_line[3].passed == 1 and by_line[3].failed == 0

    def test_spectra_returned_sorted_by_line(self) -> None:
        result = _mk_result(
            outcomes=[("t1", True)],
            line_hits={5: {"t1"}, 2: {"t1"}, 9: {"t1"}},
        )
        lines = [s.line for s in build_spectra(result)]
        assert lines == [2, 5, 9]

    def test_unknown_test_id_in_line_hits_does_not_crash(self) -> None:
        # A line context references a test id we don't have in outcomes
        # (shouldn't happen in practice but must not blow up).
        result = _mk_result(
            outcomes=[("known", True)],
            line_hits={1: {"unknown"}, 2: {"known"}},
        )
        by_line = {s.line: s for s in build_spectra(result)}
        assert by_line[1].passed == 0 and by_line[1].failed == 0
        assert by_line[2].passed == 1


class TestBuildReport:
    def test_report_includes_both_rankings_and_json_serializable(self) -> None:
        result = _mk_result(
            outcomes=[("t1", True), ("t2", False)],
            line_hits={5: {"t2"}, 6: {"t1", "t2"}},
        )
        report = build_report(result)
        assert report.total_passed == 1 and report.total_failed == 1
        # line 5 is exclusive to failing test -> max Tarantula score
        top_tarantula = report.ranking_tarantula[0]
        assert top_tarantula.line == 5 and top_tarantula.score == 1.0
        # to_json must round-trip through JSON without error
        import json
        js = json.dumps(report.to_json())
        assert "ranking" in js
        assert "tarantula" in js
        assert "ochiai" in js

    def test_report_passing_and_failing_tests_are_lists(self) -> None:
        result = _mk_result(
            outcomes=[("t1", True), ("t2", False), ("t3", True)],
            line_hits={},
        )
        report = build_report(result)
        assert report.passing_tests == ["t1", "t3"]
        assert report.failing_tests == ["t2"]
