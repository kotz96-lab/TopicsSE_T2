"""Run a task's tests against a chosen implementation and collect
per-test coverage.

We use `coverage.py` with `--dynamic-context=test_function` so each executed
line records which test IDs exercised it — that's the per-test spectrum
needed for Tarantula.

Implementation of `run_with_coverage()` is deferred until week 2 when the
first real benchmark method is in place. The stub below documents the
expected shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestOutcome:
    test_id: str        # e.g. "test_smoke.py::test_empty_list"
    passed: bool
    error_message: str = ""


@dataclass
class ExecutionResult:
    task_id: str
    outcomes: list[TestOutcome] = field(default_factory=list)
    # line_no -> set of test_ids that executed that line
    line_hits: dict[int, set[str]] = field(default_factory=dict)

    @property
    def passing_tests(self) -> list[str]:
        return [o.test_id for o in self.outcomes if o.passed]

    @property
    def failing_tests(self) -> list[str]:
        return [o.test_id for o in self.outcomes if not o.passed]


def run_with_coverage(task_dir: Path, use_buggy: bool = True) -> ExecutionResult:
    """Run all `test_*.py` in `task_dir` against buggy.py or original.py,
    return outcomes + per-line/per-test hit map.

    TODO(week 2): implement using `coverage.Coverage(context=...)`.
    Design sketch:
      1. Symlink/copy the chosen module to a known name so tests import it.
      2. Iterate tests via pytest's collect API OR run pytest with
         `--cov` and parse the resulting .coverage SQLite file for contexts.
      3. Return line_hits keyed by 1-indexed line number.
    """
    raise NotImplementedError("run_with_coverage: implement in week 2")
