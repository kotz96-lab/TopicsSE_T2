"""Infrastructure tests for Tarantula suspiciousness calculation.

Every test uses Arrange-Act-Assert and covers one specific property.
"""

from src.sbfl.tarantula import (
    LineSpectrum,
    ochiai,
    rank_lines,
    tarantula,
)


class TestTarantulaFormula:
    def test_line_hit_only_by_failing_tests_gets_max_suspiciousness(self) -> None:
        # Arrange
        failed, passed, total_failed, total_passed = 3, 0, 3, 5
        # Act
        score = tarantula(failed, passed, total_failed, total_passed)
        # Assert
        assert score == 1.0

    def test_line_hit_only_by_passing_tests_gets_zero_suspiciousness(self) -> None:
        failed, passed, total_failed, total_passed = 0, 5, 3, 5
        score = tarantula(failed, passed, total_failed, total_passed)
        assert score == 0.0

    def test_line_never_executed_returns_zero(self) -> None:
        assert tarantula(0, 0, 3, 5) == 0.0

    def test_no_failing_tests_at_all_returns_zero(self) -> None:
        # If total_failed == 0 there is no fault to localize.
        assert tarantula(0, 4, 0, 4) == 0.0

    def test_equal_pass_fail_ratio_gives_half(self) -> None:
        # Executed by all tests -> ratio_f = ratio_p = 1 -> 1 / (1+1) = 0.5
        assert tarantula(3, 5, 3, 5) == 0.5


class TestOchiaiFormula:
    def test_line_hit_only_by_failing_tests_gets_one(self) -> None:
        # All 3 failing tests hit line, no passing tests hit it, total 3 fails.
        # ochiai = 3 / sqrt(3 * (3+0)) = 3/3 = 1.0
        assert ochiai(3, 0, 3, 5) == 1.0

    def test_line_never_failed_returns_zero(self) -> None:
        assert ochiai(0, 5, 3, 5) == 0.0


class TestRankLines:
    def test_ranking_orders_by_score_descending(self) -> None:
        spectra = [
            LineSpectrum(line=1, failed=0, passed=2),   # score 0
            LineSpectrum(line=2, failed=2, passed=0),   # score 1
            LineSpectrum(line=3, failed=1, passed=1),   # score 0.5
        ]
        ranking = rank_lines(spectra, total_failed=2, total_passed=2)
        lines = [row.line for row in ranking]
        assert lines == [2, 3, 1]

    def test_ties_broken_by_line_ascending(self) -> None:
        spectra = [
            LineSpectrum(line=5, failed=1, passed=0),   # score 1
            LineSpectrum(line=2, failed=1, passed=0),   # score 1
            LineSpectrum(line=9, failed=0, passed=1),   # score 0
        ]
        ranking = rank_lines(spectra, total_failed=1, total_passed=1)
        assert [r.line for r in ranking] == [2, 5, 9]
