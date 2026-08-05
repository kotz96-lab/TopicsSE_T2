"""Stage 4 — parse raw LLM responses and compute the assignment metrics
per model, per condition, and overall.

Reads:
    results/raw/{task}__{model_slug}__cond{X}.json   — full OpenRouter
        response bodies (or error stubs written by scripts/run_llm.py)
    benchmark/methods/{task}/meta.json               — ground-truth
        `faulty_lines` + `faulty_region` labels.

Writes:
    results/parsed/{task}__{model_slug}__cond{X}.json  — ParsedResponse per call
    results/metrics/per_call.csv                        — one row per call
    results/metrics/summary.json                        — nested dict:
        {
          "overall": MetricSummary,
          "by_model": {model: MetricSummary},
          "by_condition": {condition: MetricSummary},
          "by_model_condition": {model: {condition: MetricSummary}},
        }

Usage:
    python -m scripts.compute_metrics
    python -m scripts.compute_metrics --only HE_003_below_zero
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.benchmark.loader import load_task                        # noqa: E402
from src.llm.openrouter import extract_text                       # noqa: E402
from src.metrics.scoring import ScoreableCall, summarize          # noqa: E402
from src.parsing.response_parser import parse                     # noqa: E402


RAW_DIR = REPO_ROOT / "results" / "raw"
PARSED_DIR = REPO_ROOT / "results" / "parsed"
METRICS_DIR = REPO_ROOT / "results" / "metrics"
BENCHMARK_ROOT = REPO_ROOT / "benchmark" / "methods"


# Filename shape: {task_id}__{model_slug}__cond{X}.json
RAW_FILE_RE = re.compile(r"^(?P<task>.+?)__(?P<model>.+?)__cond(?P<cond>[A-D])\.json$")


def _iter_raw_files(only_task: str | None) -> list[Path]:
    paths = []
    for p in sorted(RAW_DIR.glob("*.json")):
        m = RAW_FILE_RE.match(p.name)
        if not m:
            continue
        if only_task and m.group("task") != only_task:
            continue
        paths.append(p)
    return paths


def _extract_response_text(raw_body: dict) -> str:
    """Pull the assistant message text; empty string if unavailable."""
    if "error" in raw_body:
        return ""
    try:
        return extract_text(raw_body) or ""
    except Exception:
        return ""


def _build_scoreable(raw_path: Path, ground_truth_cache: dict[str, dict]) -> ScoreableCall | None:
    m = RAW_FILE_RE.match(raw_path.name)
    if not m:
        return None
    task_id, model_slug, cond = m.group("task"), m.group("model"), m.group("cond")
    if task_id not in ground_truth_cache:
        task_dir = BENCHMARK_ROOT / task_id
        if not task_dir.exists():
            return None
        task = load_task(task_dir)
        ground_truth_cache[task_id] = task.meta

    meta = ground_truth_cache[task_id]

    raw_body = json.loads(raw_path.read_text(encoding="utf-8"))
    text = _extract_response_text(raw_body)
    parsed = parse(text)

    # Persist the parsed response for offline inspection.
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    (PARSED_DIR / raw_path.name).write_text(
        json.dumps({
            "task_id": task_id, "model_slug": model_slug, "condition": cond,
            "is_valid": parsed.is_valid,
            "top_1_line": parsed.top_1_line,
            "top_3_lines": parsed.top_3_lines,
            "faulty_region": parsed.faulty_region,
            "explanation": parsed.explanation,
            "parse_error": parsed.parse_error,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return ScoreableCall(
        task_id=task_id,
        model=model_slug,
        condition=cond,
        is_valid=parsed.is_valid,
        top_1_line=parsed.top_1_line,
        top_3_lines=tuple(parsed.top_3_lines),
        predicted_region=parsed.faulty_region,
        faulty_lines=tuple(meta.get("faulty_lines", [])),
        faulty_region_label=str(meta.get("faulty_region", "")),
    )


def _write_per_call_csv(calls: list[ScoreableCall]) -> Path:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    out = METRICS_DIR / "per_call.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "task_id", "model", "condition", "is_valid",
            "top_1_line", "top_3_lines", "faulty_lines",
            "top1_hit", "top3_hit", "region_hit", "reciprocal_rank",
        ])
        from src.metrics.scoring import (
            reciprocal_rank, region_hit, top1_hit, top3_hit,
        )
        for c in calls:
            w.writerow([
                c.task_id, c.model, c.condition, int(c.is_valid),
                c.top_1_line if c.top_1_line is not None else "",
                "|".join(str(x) for x in c.top_3_lines),
                "|".join(str(x) for x in c.faulty_lines),
                int(top1_hit(c)), int(top3_hit(c)), int(region_hit(c)),
                f"{reciprocal_rank(c):.4f}",
            ])
    return out


def _summary_dict(calls: list[ScoreableCall]) -> dict:
    return asdict(summarize(calls))


def _write_summary(calls: list[ScoreableCall]) -> Path:
    by_model: dict[str, list[ScoreableCall]] = defaultdict(list)
    by_cond: dict[str, list[ScoreableCall]] = defaultdict(list)
    by_mc: dict[tuple[str, str], list[ScoreableCall]] = defaultdict(list)
    for c in calls:
        by_model[c.model].append(c)
        by_cond[c.condition].append(c)
        by_mc[(c.model, c.condition)].append(c)

    payload = {
        "n_calls": len(calls),
        "overall": _summary_dict(calls),
        "by_model": {m: _summary_dict(cs) for m, cs in sorted(by_model.items())},
        "by_condition": {c: _summary_dict(cs) for c, cs in sorted(by_cond.items())},
        "by_model_condition": {
            m: {c: _summary_dict(cs) for (mm, c), cs in sorted(by_mc.items()) if mm == m}
            for m in sorted(by_model)
        },
    }
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    out = METRICS_DIR / "summary.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Restrict to a single task_id.")
    args = parser.parse_args(argv)

    if not RAW_DIR.exists():
        print(f"No raw responses at {RAW_DIR}. Run scripts/run_llm.py first.")
        return 1

    paths = _iter_raw_files(args.only)
    if not paths:
        print("No matching raw responses found.")
        return 1

    ground_truth_cache: dict[str, dict] = {}
    calls: list[ScoreableCall] = []
    for p in paths:
        call = _build_scoreable(p, ground_truth_cache)
        if call is not None:
            calls.append(call)

    csv_path = _write_per_call_csv(calls)
    summary_path = _write_summary(calls)

    print(f"Scored {len(calls)} calls.")
    print(f"Per-call CSV: {csv_path}")
    print(f"Summary JSON: {summary_path}")

    # Print a compact overall + per-condition table.
    summary = summarize(calls)
    print(f"\nOverall: top1={summary.top1_accuracy:.1%} "
          f"top3={summary.top3_accuracy:.1%} "
          f"region={summary.region_accuracy:.1%} "
          f"mrr={summary.mrr:.3f} "
          f"invalid={summary.invalid_rate:.1%}")

    by_cond: dict[str, list[ScoreableCall]] = defaultdict(list)
    for c in calls:
        by_cond[c.condition].append(c)
    print("\nBy condition:")
    print(f"  {'cond':4s} {'n':>4s} {'top1':>6s} {'top3':>6s} {'region':>7s} {'mrr':>6s} {'invalid':>8s}")
    for cond in sorted(by_cond):
        s = summarize(by_cond[cond])
        print(f"  {cond:4s} {s.n:>4d} {s.top1_accuracy:>6.1%} {s.top3_accuracy:>6.1%} "
              f"{s.region_accuracy:>7.1%} {s.mrr:>6.3f} {s.invalid_rate:>8.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
