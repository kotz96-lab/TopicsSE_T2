"""Stage 3 — build prompts for every (task, model, condition) combination
and optionally call OpenRouter, saving the raw response body verbatim.

Reads:
    benchmark/methods/*/           — task folders + meta.json
    results/sbfl/{task}.json       — Tarantula rankings (for conditions C/D)
    prompts/condition_*.txt        — prompt templates

Writes (always):
    results/prompts/{task}__{model_slug}__{cond}.txt   — the exact string
        that would be sent to the model.

Writes (real mode only, --dry-run skips this):
    results/raw/{task}__{model_slug}__{cond}.json      — full OpenRouter
        response body (choices, usage, model, id, ...).

Usage:
    python -m scripts.run_llm --dry-run              # just build prompts
    python -m scripts.run_llm                        # dry-run + call API
    python -m scripts.run_llm --only HE_003_below_zero
    python -m scripts.run_llm --models openai/gpt-4o-mini
    python -m scripts.run_llm --skip-existing        # don't overwrite raw/
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.benchmark.loader import BENCHMARK_ROOT, load_task              # noqa: E402
from src.llm import openrouter                                          # noqa: E402
from src.llm.prompts import PromptInputs, build_prompt                  # noqa: E402
from src.pipeline.config import CONDITIONS, load_config, model_slug     # noqa: E402


RESULTS_ROOT = REPO_ROOT / "results"
PROMPTS_OUT = RESULTS_ROOT / "prompts"
RAW_OUT = RESULTS_ROOT / "raw"
SBFL_DIR = RESULTS_ROOT / "sbfl"


def _load_sbfl(task_id: str) -> dict | None:
    p = SBFL_DIR / f"{task_id}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _build_inputs_for(task_dir: Path, condition: str) -> PromptInputs:
    task = load_task(task_dir)
    sbfl = _load_sbfl(task.task_id) or {}
    passing = list(sbfl.get("passing_tests", []))
    failing = list(sbfl.get("failing_tests", []))
    tarantula_ranking = [
        (row["line"], row["score"])
        for row in sbfl.get("ranking", {}).get("tarantula", [])
    ]

    if condition == "A":
        # Code only — clear tests + ranking so leakage is impossible.
        passing, failing, tarantula_ranking = [], [], []
    elif condition == "B":
        tarantula_ranking = []
    elif condition == "C":
        passing, failing = [], []
    elif condition == "D":
        pass  # everything on
    else:
        raise ValueError(f"unknown condition {condition!r}")

    return PromptInputs(
        spec=task.spec,
        buggy_source=task.buggy_source,
        passing_tests=passing,
        failing_tests=failing,
        sbfl_ranking=tarantula_ranking,
    )


def _out_name(task_id: str, model: str, condition: str, ext: str) -> str:
    return f"{task_id}__{model_slug(model)}__cond{condition}.{ext}"


def _run_one(
    task_dir: Path,
    model: str,
    condition: str,
    *,
    dry_run: bool,
    temperature: float,
    max_tokens: int,
    skip_existing: bool,
) -> tuple[str, str]:
    task_id = task_dir.name
    prompt_inputs = _build_inputs_for(task_dir, condition)
    prompt = build_prompt(condition, prompt_inputs)

    PROMPTS_OUT.mkdir(parents=True, exist_ok=True)
    prompt_path = PROMPTS_OUT / _out_name(task_id, model, condition, "txt")
    prompt_path.write_text(prompt, encoding="utf-8")

    if dry_run:
        return "DRY", f"prompt bytes={len(prompt)}"

    RAW_OUT.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_OUT / _out_name(task_id, model, condition, "json")
    if skip_existing and raw_path.exists():
        return "SKIP", "raw file already exists"

    call = openrouter.OpenRouterCall(
        model=model, prompt=prompt, temperature=temperature, max_tokens=max_tokens
    )
    try:
        response = openrouter.chat(call)
    except openrouter.OpenRouterError as e:
        # Persist the error so we still have a record; parse stage will
        # count these toward the invalid-output rate.
        raw_path.write_text(
            json.dumps({"error": str(e), "call": {"model": model, "condition": condition}}, indent=2),
            encoding="utf-8",
        )
        return "ERR", str(e)[:150]

    raw_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    text_len = len(openrouter.extract_text(response) or "")
    return "OK", f"response chars={text_len}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Only build prompts; do not call the LLM.")
    parser.add_argument("--only", help="Restrict to a single task_id.")
    parser.add_argument("--models", help="Comma-separated model IDs (overrides config).")
    parser.add_argument("--conditions", default=",".join(CONDITIONS),
                        help="Comma-separated conditions to run.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Do not overwrite existing raw/ files.")
    parser.add_argument("--sleep-between", type=float, default=0.0,
                        help="Seconds to sleep between API calls (rate limits).")
    args = parser.parse_args(argv)

    # Optional dotenv load — if the file is missing that's fine for --dry-run.
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    cfg = load_config()
    models = tuple(m.strip() for m in args.models.split(",")) if args.models else cfg.models
    conditions = tuple(c.strip() for c in args.conditions.split(","))

    if not args.dry_run and not os.environ.get("OPENROUTER_API_KEY"):
        print("Refusing to make API calls without OPENROUTER_API_KEY.")
        print("Either set it in .env or pass --dry-run to just build prompts.")
        return 2

    all_dirs = sorted(d for d in BENCHMARK_ROOT.iterdir() if d.is_dir())
    if args.only:
        all_dirs = [d for d in all_dirs if d.name == args.only]
        if not all_dirs:
            print(f"No task named {args.only!r}")
            return 1

    total = len(all_dirs) * len(models) * len(conditions)
    print(f"Running {total} combinations: "
          f"{len(all_dirs)} tasks × {len(models)} models × {len(conditions)} conditions"
          + (" (dry-run)" if args.dry_run else ""))

    counters = {"OK": 0, "DRY": 0, "SKIP": 0, "ERR": 0}
    for i, d in enumerate(all_dirs):
        for model in models:
            for cond in conditions:
                status, msg = _run_one(
                    d, model, cond,
                    dry_run=args.dry_run,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    skip_existing=args.skip_existing,
                )
                counters[status] = counters.get(status, 0) + 1
                print(f"[{status}] {d.name:30s} {model:35s} cond={cond}  {msg[:80]}")
                if not args.dry_run and status == "OK" and args.sleep_between > 0:
                    time.sleep(args.sleep_between)

    print("\nSummary:")
    for k, v in counters.items():
        print(f"  {k}: {v}")
    return 0 if counters.get("ERR", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
