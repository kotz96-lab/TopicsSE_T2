"""Metrics required by the assignment (Section 5).

All metrics operate over a collection of `ScoreableCall` records, each of
which pairs a parsed model prediction with the ground-truth faulty region.

Metrics implemented here:
  * Top-1 exact-line accuracy
  * Top-3 accuracy
  * Region accuracy (top_1_line falls within any faulty line, OR the
    predicted region text contains the ground-truth region label)
  * Mean reciprocal rank (over top_3_lines; 0 if the true line is not in
    the list)
  * Invalid-output rate
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreableCall:
    task_id: str
    model: str
    condition: str
    is_valid: bool
    top_1_line: int | None
    top_3_lines: tuple[int, ...]
    predicted_region: str
    faulty_lines: tuple[int, ...]
    faulty_region_label: str


def top1_hit(call: ScoreableCall) -> bool:
    return call.is_valid and call.top_1_line in call.faulty_lines


def top3_hit(call: ScoreableCall) -> bool:
    if not call.is_valid:
        return False
    return any(line in call.faulty_lines for line in call.top_3_lines)


def region_hit(call: ScoreableCall) -> bool:
    if not call.is_valid:
        return False
    if call.top_1_line in call.faulty_lines:
        return True
    label = (call.faulty_region_label or "").strip().lower()
    if label and label in (call.predicted_region or "").lower():
        return True
    return False


def reciprocal_rank(call: ScoreableCall) -> float:
    if not call.is_valid or not call.top_3_lines:
        return 0.0
    for i, line in enumerate(call.top_3_lines, start=1):
        if line in call.faulty_lines:
            return 1.0 / i
    return 0.0


@dataclass(frozen=True)
class MetricSummary:
    n: int
    top1_accuracy: float
    top3_accuracy: float
    region_accuracy: float
    mrr: float
    invalid_rate: float


def summarize(calls: list[ScoreableCall]) -> MetricSummary:
    if not calls:
        return MetricSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0)
    n = len(calls)
    invalid = sum(1 for c in calls if not c.is_valid)
    top1 = sum(1 for c in calls if top1_hit(c))
    top3 = sum(1 for c in calls if top3_hit(c))
    region = sum(1 for c in calls if region_hit(c))
    mrr = sum(reciprocal_rank(c) for c in calls) / n
    return MetricSummary(
        n=n,
        top1_accuracy=top1 / n,
        top3_accuracy=top3 / n,
        region_accuracy=region / n,
        mrr=mrr,
        invalid_rate=invalid / n,
    )
