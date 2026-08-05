"""Fabricate a full `results/raw/` directory of fake OpenRouter responses
so the parsing + metrics pipeline can be exercised end-to-end without
spending API credits.

We use the SBFL Tarantula ranking as a stand-in "model":
    * with SBFL info (conditions C, D) the fake model picks the top-1
      Tarantula line as top_1_line (this is a very SBFL-adherent baseline)
    * without SBFL info (conditions A, B) it picks a plausible line —
      the last line inside the function body (often `return False`)
    * for one out of every 15 combinations we deliberately emit malformed
      JSON so the invalid-output rate is > 0 and the parser gets exercised.

This is ONLY for exercising the metrics pipeline. It is NOT a real
experiment — real numbers will come from `scripts/run_llm.py` once an
API key is set up.

Usage:
    python -m scripts.seed_synthetic_responses
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.benchmark.loader import BENCHMARK_ROOT, load_task    # noqa: E402
from src.pipeline.config import CONDITIONS, model_slug        # noqa: E402


RAW_DIR = REPO_ROOT / "results" / "raw"
SBFL_DIR = REPO_ROOT / "results" / "sbfl"

# Match the default models in pipeline.config for parity with a real run.
FAKE_MODELS = ("openai/gpt-4o-mini", "anthropic/claude-3.5-haiku")


def _fake_body(prediction: dict) -> dict:
    """Wrap a JSON string in a minimal OpenRouter-shaped response body."""
    return {
        "id": "fake-response",
        "model": "synthetic",
        "choices": [{
            "message": {"role": "assistant", "content": json.dumps(prediction)},
            "finish_reason": "stop",
            "index": 0,
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _malformed_body() -> dict:
    """A body whose content isn't valid JSON, to exercise the invalid-rate path."""
    return {
        "id": "fake-malformed",
        "model": "synthetic",
        "choices": [{
            "message": {"role": "assistant",
                        "content": "I think the bug is around the loop condition. Sorry, no JSON today."},
            "finish_reason": "stop",
            "index": 0,
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _fake_prediction(task, cond: str, i: int) -> dict:
    """Choose a top_1 / top_3 based on what info the condition would expose."""
    sbfl_path = SBFL_DIR / f"{task.task_id}.json"
    tarantula_top3: list[int] = []
    if sbfl_path.exists():
        sbfl = json.loads(sbfl_path.read_text(encoding="utf-8"))
        tarantula_top3 = [row["line"] for row in sbfl["ranking"]["tarantula"][:3]]

    faulty = task.meta.get("faulty_lines", [1])
    faulty_region = task.meta.get("faulty_region", "unspecified region")
    last_body_line = len(task.buggy_source.splitlines())

    if cond in ("C", "D") and tarantula_top3:
        # SBFL-adherent baseline: pick top-1 tarantula
        top_1 = tarantula_top3[0]
        top_3 = (tarantula_top3 + [top_1 + 1, top_1 + 2])[:3]
    else:
        # No SBFL info: alternate between an obvious wrong guess and the
        # true line, so the synthetic accuracy sits somewhere between 0
        # and 100% — good for exercising the metrics.
        if i % 2 == 0:
            top_1 = last_body_line
        else:
            top_1 = faulty[0]
        top_3 = [top_1, max(1, top_1 - 1), max(1, top_1 - 2)]

    return {
        "top_1_line": top_1,
        "top_3_lines": top_3,
        "faulty_region": faulty_region,
        "explanation": f"Synthetic prediction for condition {cond}.",
    }


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    task_dirs = sorted(d for d in BENCHMARK_ROOT.iterdir() if d.is_dir())
    n_written = n_bad = 0
    i = 0
    for task_dir in task_dirs:
        task = load_task(task_dir)
        for model in FAKE_MODELS:
            for cond in CONDITIONS:
                i += 1
                fname = f"{task.task_id}__{model_slug(model)}__cond{cond}.json"
                out = RAW_DIR / fname
                if i % 15 == 0:
                    body = _malformed_body()
                    n_bad += 1
                else:
                    body = _fake_body(_fake_prediction(task, cond, i))
                out.write_text(json.dumps(body, indent=2), encoding="utf-8")
                n_written += 1
    print(f"Wrote {n_written} synthetic responses ({n_bad} intentionally malformed) to {RAW_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
