"""Infrastructure tests for the metrics used to answer the RQs."""

from src.metrics.scoring import (
    ScoreableCall,
    reciprocal_rank,
    region_hit,
    summarize,
    top1_hit,
    top3_hit,
)


def _call(
    *,
    is_valid: bool = True,
    top_1: int | None = 5,
    top_3: tuple[int, ...] = (5, 7, 9),
    region: str = "loop bound",
    faulty_lines: tuple[int, ...] = (5,),
    faulty_region: str = "loop bound",
) -> ScoreableCall:
    return ScoreableCall(
        task_id="task",
        model="m",
        condition="A",
        is_valid=is_valid,
        top_1_line=top_1,
        top_3_lines=top_3,
        predicted_region=region,
        faulty_lines=faulty_lines,
        faulty_region_label=faulty_region,
    )


class TestTop1Hit:
    def test_correct_line_is_a_hit(self) -> None:
        assert top1_hit(_call(top_1=5, faulty_lines=(5,)))

    def test_wrong_line_is_a_miss(self) -> None:
        assert not top1_hit(_call(top_1=6, faulty_lines=(5,)))

    def test_invalid_response_is_never_a_hit(self) -> None:
        assert not top1_hit(_call(is_valid=False, top_1=5))


class TestTop3Hit:
    def test_correct_line_anywhere_in_top3_counts(self) -> None:
        assert top3_hit(_call(top_3=(1, 2, 5), faulty_lines=(5,)))

    def test_no_faulty_line_in_top3_is_miss(self) -> None:
        assert not top3_hit(_call(top_3=(1, 2, 3), faulty_lines=(5,)))


class TestRegionHit:
    def test_exact_line_match_counts_as_region_hit(self) -> None:
        assert region_hit(_call(top_1=5, faulty_lines=(5,)))

    def test_region_label_substring_counts(self) -> None:
        call = _call(top_1=99, region="the loop bound is off", faulty_region="loop bound")
        assert region_hit(call)

    def test_unrelated_prediction_is_not_a_region_hit(self) -> None:
        call = _call(top_1=99, region="return statement", faulty_region="loop bound")
        assert not region_hit(call)


class TestReciprocalRank:
    def test_first_position_gives_one(self) -> None:
        assert reciprocal_rank(_call(top_3=(5, 6, 7), faulty_lines=(5,))) == 1.0

    def test_second_position_gives_half(self) -> None:
        assert reciprocal_rank(_call(top_3=(6, 5, 7), faulty_lines=(5,))) == 0.5

    def test_missing_from_top3_gives_zero(self) -> None:
        assert reciprocal_rank(_call(top_3=(6, 7, 8), faulty_lines=(5,))) == 0.0


class TestSummarize:
    def test_empty_input_returns_zeros(self) -> None:
        summary = summarize([])
        assert summary.n == 0
        assert summary.top1_accuracy == 0.0
        assert summary.invalid_rate == 0.0

    def test_summary_computes_expected_rates(self) -> None:
        calls = [
            _call(top_1=5, top_3=(5, 6, 7), faulty_lines=(5,)),   # top1 hit
            _call(top_1=6, top_3=(6, 5, 7), faulty_lines=(5,)),   # top3 hit, mrr .5
            _call(is_valid=False, top_1=None, top_3=()),           # invalid
        ]
        summary = summarize(calls)
        assert summary.n == 3
        assert summary.top1_accuracy == 1 / 3
        assert summary.top3_accuracy == 2 / 3
        assert summary.invalid_rate == 1 / 3
        # MRR = (1 + 0.5 + 0) / 3
        assert abs(summary.mrr - 0.5) < 1e-9
