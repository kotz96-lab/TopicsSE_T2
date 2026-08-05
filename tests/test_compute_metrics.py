"""Tests for scripts/compute_metrics.

Uses a temporary results/raw/ directory populated with synthetic response
bodies so the whole raw -> parsed -> metrics flow can be exercised
without touching the real experiment results.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import compute_metrics


BENCHMARK_TASK = "HE_000_has_close_elements"
FAULTY_LINE = 6  # matches meta.json for this task


def _wrap_response(prediction: dict) -> dict:
    return {
        "id": "test", "model": "test-model",
        "choices": [{"message": {"role": "assistant",
                                  "content": json.dumps(prediction)}}],
    }


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    """Point compute_metrics at a temp raw/ + parsed/ + metrics/ tree."""
    raw = tmp_path / "raw"
    parsed = tmp_path / "parsed"
    metrics = tmp_path / "metrics"
    raw.mkdir()
    monkeypatch.setattr(compute_metrics, "RAW_DIR", raw)
    monkeypatch.setattr(compute_metrics, "PARSED_DIR", parsed)
    monkeypatch.setattr(compute_metrics, "METRICS_DIR", metrics)
    return raw


def _write_response(raw_dir: Path, cond: str, model: str, prediction: dict) -> None:
    fname = f"{BENCHMARK_TASK}__{model}__cond{cond}.json"
    (raw_dir / fname).write_text(json.dumps(_wrap_response(prediction)), encoding="utf-8")


class TestBuildScoreable:
    def test_valid_response_scores_correctly_when_line_matches(self, raw_dir) -> None:
        # A response whose top_1_line matches the ground truth should hit.
        _write_response(raw_dir, "A", "vendor__model", {
            "top_1_line": FAULTY_LINE,
            "top_3_lines": [FAULTY_LINE, 1, 2],
            "faulty_region": "distance comparison",
            "explanation": "off-by-one on the comparison",
        })
        path = next(raw_dir.glob("*.json"))
        call = compute_metrics._build_scoreable(path, {})
        assert call is not None
        assert call.is_valid
        assert call.top_1_line == FAULTY_LINE
        assert FAULTY_LINE in call.faulty_lines

    def test_malformed_response_marked_invalid(self, raw_dir) -> None:
        fname = f"{BENCHMARK_TASK}__vendor__model__condA.json"
        (raw_dir / fname).write_text(json.dumps({
            "choices": [{"message": {"content": "no JSON here, just prose"}}],
        }), encoding="utf-8")
        path = raw_dir / fname
        call = compute_metrics._build_scoreable(path, {})
        assert call is not None
        assert not call.is_valid

    def test_error_stub_from_run_llm_marked_invalid(self, raw_dir) -> None:
        fname = f"{BENCHMARK_TASK}__vendor__model__condA.json"
        (raw_dir / fname).write_text(json.dumps({
            "error": "rate limit exceeded",
            "call": {"model": "x", "condition": "A"},
        }), encoding="utf-8")
        path = raw_dir / fname
        call = compute_metrics._build_scoreable(path, {})
        assert call is not None
        assert not call.is_valid


class TestFullPipeline:
    def test_end_to_end_produces_csv_and_summary(self, raw_dir) -> None:
        # One perfect + one miss = 50% top1 for the model.
        _write_response(raw_dir, "A", "vendor__model", {
            "top_1_line": FAULTY_LINE, "top_3_lines": [FAULTY_LINE],
            "faulty_region": "x", "explanation": "y",
        })
        _write_response(raw_dir, "B", "vendor__model", {
            "top_1_line": 999, "top_3_lines": [999],
            "faulty_region": "x", "explanation": "y",
        })
        rc = compute_metrics.main([])
        assert rc == 0
        summary = json.loads((compute_metrics.METRICS_DIR / "summary.json").read_text())
        assert summary["n_calls"] == 2
        assert summary["overall"]["top1_accuracy"] == 0.5
        csv_text = (compute_metrics.METRICS_DIR / "per_call.csv").read_text()
        assert "task_id" in csv_text
        assert BENCHMARK_TASK in csv_text
