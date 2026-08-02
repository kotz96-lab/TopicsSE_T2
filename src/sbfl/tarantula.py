"""Spectrum-based fault localization: Tarantula (+ a couple of extras).

Input shape: for each executable line s we know
  failed(s)     = # failing tests that executed s
  passed(s)     = # passing tests that executed s
  total_failed  = # failing tests
  total_passed  = # passing tests

Tarantula suspiciousness:
                       failed(s) / total_failed
    susp(s) = ------------------------------------------------
              failed(s)/total_failed + passed(s)/total_passed

Convention: if a line was not executed at all (failed(s) == 0 and
passed(s) == 0) we return 0.0 so it sinks to the bottom of the ranking.
When total_failed == 0 there is no bug to localize, we return 0.0 for all.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineSpectrum:
    line: int          # 1-indexed line number
    failed: int
    passed: int


@dataclass(frozen=True)
class SuspiciousnessRow:
    line: int
    score: float
    failed: int
    passed: int


def tarantula(failed: int, passed: int, total_failed: int, total_passed: int) -> float:
    if total_failed == 0:
        return 0.0
    if failed == 0 and passed == 0:
        return 0.0
    fail_ratio = failed / total_failed
    pass_ratio = (passed / total_passed) if total_passed > 0 else 0.0
    denom = fail_ratio + pass_ratio
    if denom == 0:
        return 0.0
    return fail_ratio / denom


def ochiai(failed: int, passed: int, total_failed: int, total_passed: int) -> float:
    # sqrt(total_failed * (failed + passed)); classic Ochiai formula.
    from math import sqrt
    if total_failed == 0 or failed == 0:
        return 0.0
    denom = sqrt(total_failed * (failed + passed))
    return failed / denom if denom else 0.0


def rank_lines(
    spectra: list[LineSpectrum],
    total_failed: int,
    total_passed: int,
    formula=tarantula,
) -> list[SuspiciousnessRow]:
    """Return rows sorted by score DESC, tie-broken by line ASC."""
    rows = [
        SuspiciousnessRow(
            line=s.line,
            score=formula(s.failed, s.passed, total_failed, total_passed),
            failed=s.failed,
            passed=s.passed,
        )
        for s in spectra
    ]
    rows.sort(key=lambda r: (-r.score, r.line))
    return rows
