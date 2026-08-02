"""Stage 1 — validate the benchmark dataset.

For each task under `benchmark/methods/`:
  * verify the folder shape (original.py, buggy.py, spec.md, meta.json, ≥1 test_*.py)
  * verify original.py passes all tests
  * verify buggy.py fails at least one test
  * count tests to confirm ≥10

Prints a summary table; exits non-zero if any check fails.

Usage:
    python -m scripts.build_dataset
"""

from __future__ import annotations

import sys

from src.benchmark.loader import BENCHMARK_ROOT, load_all


def main() -> int:
    if not BENCHMARK_ROOT.exists():
        print(f"[!] Benchmark root does not exist yet: {BENCHMARK_ROOT}")
        print("    Create it and add task folders before running this script.")
        return 1
    tasks = load_all()
    if not tasks:
        print("[!] No tasks found. Add HumanEval-style methods to benchmark/methods/.")
        return 1
    print(f"Found {len(tasks)} task(s):")
    for t in tasks:
        n_tests = len(t.test_files)
        faulty = t.meta.get("faulty_lines", [])
        print(f"  - {t.task_id:30s}  tests={n_tests:2d}  faulty_lines={faulty}")
    # TODO(week 2): actually run the test suites and enforce the pass/fail invariants.
    return 0


if __name__ == "__main__":
    sys.exit(main())
