"""Stage 2 — run tests with per-test coverage and compute Tarantula
rankings for every buggy method.

Writes one JSON per task to `results/sbfl/{task_id}.json`:

    {
      "task_id": "...",
      "total_failed": 3,
      "total_passed": 7,
      "passing_tests": [...],
      "failing_tests": [...],
      "ranking": [
        {"line": 12, "score": 1.0, "failed": 3, "passed": 1},
        ...
      ]
    }

Usage:
    python -m scripts.run_sbfl
"""

from __future__ import annotations

import sys


def main() -> int:
    # TODO(week 2): wire src.testing.runner.run_with_coverage +
    # src.sbfl.tarantula.rank_lines and dump JSON per task.
    print("run_sbfl: not implemented yet — see TODO in src/testing/runner.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
