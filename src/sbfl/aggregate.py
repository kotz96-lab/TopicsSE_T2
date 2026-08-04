"""Turn a `runner.ExecutionResult` into per-line Tarantula rankings + the
serializable JSON payload the LLM will consume in condition C/D.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.sbfl.tarantula import LineSpectrum, SuspiciousnessRow, ochiai, rank_lines, tarantula
from src.testing.runner import ExecutionResult


@dataclass(frozen=True)
class SbflReport:
    task_id: str
    total_passed: int
    total_failed: int
    passing_tests: list[str]
    failing_tests: list[str]
    ranking_tarantula: list[SuspiciousnessRow]
    ranking_ochiai: list[SuspiciousnessRow]

    def to_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "passing_tests": list(self.passing_tests),
            "failing_tests": list(self.failing_tests),
            "ranking": {
                "tarantula": [_row_to_dict(r) for r in self.ranking_tarantula],
                "ochiai": [_row_to_dict(r) for r in self.ranking_ochiai],
            },
        }


def _row_to_dict(row: SuspiciousnessRow) -> dict[str, Any]:
    return {
        "line": row.line,
        "score": round(row.score, 6),
        "failed": row.failed,
        "passed": row.passed,
    }


def build_spectra(result: ExecutionResult) -> list[LineSpectrum]:
    """For each executed line, count how many passing / failing tests
    executed it."""
    passing = set(result.passing_tests)
    failing = set(result.failing_tests)
    spectra: list[LineSpectrum] = []
    for line, tests in sorted(result.line_hits.items()):
        n_pass = sum(1 for t in tests if t in passing)
        n_fail = sum(1 for t in tests if t in failing)
        spectra.append(LineSpectrum(line=line, failed=n_fail, passed=n_pass))
    return spectra


def build_report(result: ExecutionResult) -> SbflReport:
    spectra = build_spectra(result)
    return SbflReport(
        task_id=result.task_id,
        total_passed=result.total_passed,
        total_failed=result.total_failed,
        passing_tests=result.passing_tests,
        failing_tests=result.failing_tests,
        ranking_tarantula=rank_lines(spectra, result.total_failed, result.total_passed, formula=tarantula),
        ranking_ochiai=rank_lines(spectra, result.total_failed, result.total_passed, formula=ochiai),
    )
