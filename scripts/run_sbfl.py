"""Stage 2 — run each task's tests with per-test coverage and compute
Tarantula (and Ochiai) rankings.

Reads:
    benchmark/methods/*/

Writes:
    results/sbfl/{task_id}.json      — full report used by the LLM stage
    results/coverage/{task_id}.junit  — raw JUnit outcomes (for debugging)

The JSON payload shape is documented in src/sbfl/aggregate.py::SbflReport.

Usage:
    python -m scripts.run_sbfl                     # all tasks
    python -m scripts.run_sbfl HE_003_below_zero   # single task
    python -m scripts.run_sbfl --skip-existing     # skip tasks already computed
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.benchmark.loader import BENCHMARK_ROOT, load_task           # noqa: E402
from src.sbfl.aggregate import build_report                          # noqa: E402
from src.testing.runner import run_with_coverage                     # noqa: E402


RESULTS_ROOT = REPO_ROOT / "results"
SBFL_DIR = RESULTS_ROOT / "sbfl"
COVERAGE_DIR = RESULTS_ROOT / "coverage"


def _process_task(task_dir: Path) -> tuple[bool, str]:
    task = load_task(task_dir)
    result = run_with_coverage(task_dir, use_buggy=True)

    # Sanity checks — a good SBFL run needs at least one failing test.
    if result.total_failed == 0:
        return False, f"no failing tests (mutation may be equivalent) for {task.task_id}"
    if not result.line_hits:
        return False, f"no line coverage captured for {task.task_id}"

    report = build_report(result)
    out_path = SBFL_DIR / f"{task.task_id}.json"
    out_path.write_text(json.dumps(report.to_json(), indent=2) + "\n", encoding="utf-8")

    # Copy the JUnit and coverage files for offline debugging.
    junit_src = task_dir / "junit.xml"
    cov_src = task_dir / ".coverage"
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    if junit_src.exists():
        shutil.copy2(junit_src, COVERAGE_DIR / f"{task.task_id}.junit.xml")
    if cov_src.exists():
        shutil.copy2(cov_src, COVERAGE_DIR / f"{task.task_id}.coverage")

    top = report.ranking_tarantula[:3]
    top_str = ", ".join(f"line {r.line}(s={r.score:.2f})" for r in top)
    return True, f"tests {result.total_passed}p/{result.total_failed}f | top-3 tarantula: {top_str}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("only", nargs="?", help="Single task_id to run.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip tasks whose result JSON already exists.")
    args = parser.parse_args(argv)

    SBFL_DIR.mkdir(parents=True, exist_ok=True)
    all_dirs = sorted(d for d in BENCHMARK_ROOT.iterdir() if d.is_dir())
    if args.only:
        all_dirs = [d for d in all_dirs if d.name == args.only]
        if not all_dirs:
            print(f"No task named {args.only!r}")
            return 1

    ok = 0
    failures: list[tuple[str, str]] = []
    for d in all_dirs:
        out_path = SBFL_DIR / f"{d.name}.json"
        if args.skip_existing and out_path.exists():
            print(f"[SKIP] {d.name}")
            continue
        try:
            success, msg = _process_task(d)
        except Exception as e:
            success, msg = False, f"exception: {e!r}"
        marker = "OK  " if success else "FAIL"
        print(f"[{marker}] {d.name:35s} {msg[:150]}")
        if success:
            ok += 1
        else:
            failures.append((d.name, msg))

    print(f"\n{ok}/{len(all_dirs)} tasks succeeded.")
    if failures:
        print("\nFailures:")
        for tid, msg in failures:
            print(f"  {tid}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
