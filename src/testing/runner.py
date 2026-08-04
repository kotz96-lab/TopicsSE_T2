"""Run a task's tests against buggy.py (or original.py) and collect
per-test line-coverage — the spectrum needed by SBFL.

Implementation notes:
  * `pytest-cov` with `--cov-context=test` tags every executed line with the
    test id that executed it. `coverage.CoverageData.contexts_by_lineno()`
    then gives us `{line_no: [context, ...]}` which we normalize into
    `{line_no: {test_id, ...}}`.
  * Test outcomes come from a JUnit XML report — cross-version reliable and
    doesn't depend on parsing pytest's stdout (which shortens differently
    depending on TTY detection).
  * When we want to test the ORIGINAL implementation we temporarily copy
    `original.py` into `buggy.py` (since the test file imports from
    `buggy`), then restore. Python's .pyc mtime check has 1-second
    granularity so we always pass `-B` and nuke `__pycache__` first.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import coverage


@dataclass
class TestOutcome:
    # Pytest would otherwise auto-collect this as a test class because of
    # the `Test` prefix.
    __test__ = False

    test_id: str
    """Normalized test id: `test_file.py::test_function` (no context suffix)."""
    passed: bool
    error_message: str = ""


@dataclass
class ExecutionResult:
    task_id: str
    outcomes: list[TestOutcome] = field(default_factory=list)
    line_hits: dict[int, set[str]] = field(default_factory=dict)
    """Line number (1-indexed against buggy.py) -> set of test ids that
    executed that line."""

    @property
    def passing_tests(self) -> list[str]:
        return sorted(o.test_id for o in self.outcomes if o.passed)

    @property
    def failing_tests(self) -> list[str]:
        return sorted(o.test_id for o in self.outcomes if not o.passed)

    @property
    def total_passed(self) -> int:
        return sum(1 for o in self.outcomes if o.passed)

    @property
    def total_failed(self) -> int:
        return sum(1 for o in self.outcomes if not o.passed)


# ---------------- context / junit parsing helpers ----------------

def _normalize_test_id(context: str) -> str:
    """Turn pytest-cov's context into a plain `test_file.py::test_name`.

    Contexts look like:
        'benchmark/methods/HE_000_.../test_has_close_elements.py::test_x|run'
        'test_below_zero.py::test_extra_01|run'
    We strip the '|run'/'|setup'/'|teardown' suffix and any leading path
    components so all IDs use the bare filename.
    """
    ctx = context.rsplit("|", 1)[0]  # drop |run / |setup / |teardown
    if "::" not in ctx:
        return ctx  # not a per-test context (e.g. module-level '')
    filename, rest = ctx.split("::", 1)
    return f"{Path(filename).name}::{rest}"


def _parse_junit(junit_path: Path) -> list[TestOutcome]:
    tree = ET.parse(junit_path)
    outcomes: list[TestOutcome] = []
    for tc in tree.iter("testcase"):
        classname = tc.get("classname") or ""
        name = tc.get("name") or ""
        # classname in JUnit typically encodes the module dotted path.
        # Reconstruct a pytest-style id: `test_file.py::test_name`.
        file_stem = classname.split(".")[-1]
        test_id = f"{file_stem}.py::{name}"
        failure = tc.find("failure") is not None or tc.find("error") is not None
        msg = ""
        for tag in ("failure", "error"):
            node = tc.find(tag)
            if node is not None:
                msg = (node.get("message") or node.text or "")[:500]
                break
        outcomes.append(TestOutcome(test_id=test_id, passed=not failure, error_message=msg))
    return outcomes


def _extract_line_hits(cov_data: coverage.CoverageData, buggy_path: Path) -> dict[int, set[str]]:
    """Read `contexts_by_lineno` for buggy.py and normalize test ids.

    Coverage.py stores file paths as absolute strings; matching by resolved
    path avoids mismatches from relative-vs-absolute or case differences on
    Windows.
    """
    target = buggy_path.resolve()
    matched_file: str | None = None
    for f in cov_data.measured_files():
        try:
            if Path(f).resolve() == target:
                matched_file = f
                break
        except OSError:
            continue
    if matched_file is None:
        return {}
    hits: dict[int, set[str]] = {}
    for line, contexts in cov_data.contexts_by_lineno(matched_file).items():
        tests = {
            _normalize_test_id(c)
            for c in contexts
            if c and "::" in c  # skip module-level '' context
        }
        if tests:
            hits[line] = tests
    return hits


# ---------------- main entry point ----------------

def run_with_coverage(task_dir: Path, *, use_buggy: bool = True) -> ExecutionResult:
    """Run the task's test file with per-test coverage against `buggy.py`
    (or, if `use_buggy=False`, temporarily against `original.py`)."""
    buggy_path = task_dir / "buggy.py"
    original_path = task_dir / "original.py"
    test_file = next(task_dir.glob("test_*.py"))

    swapped_backup: str | None = None
    if not use_buggy:
        swapped_backup = buggy_path.read_text(encoding="utf-8")
        buggy_path.write_text(original_path.read_text(encoding="utf-8"), encoding="utf-8")

    try:
        _clean(task_dir)
        cov_file = task_dir / ".coverage"
        junit_file = task_dir / "junit.xml"

        # Run pytest with per-test coverage contexts + JUnit outcomes.
        subprocess.run(
            [
                sys.executable, "-B", "-m", "pytest", test_file.name, "-q",
                "--cov=buggy", "--cov-context=test", "--cov-report=",
                f"--junitxml={junit_file.name}",
                "-p", "no:cacheprovider",
                "--tb=no",
            ],
            cwd=str(task_dir), capture_output=True, text=True, timeout=120,
        )

        if not junit_file.exists():
            raise RuntimeError(f"pytest did not produce {junit_file}")

        outcomes = _parse_junit(junit_file)

        line_hits: dict[int, set[str]] = {}
        if cov_file.exists():
            data = coverage.CoverageData(basename=str(cov_file))
            data.read()
            line_hits = _extract_line_hits(data, buggy_path)
    finally:
        if swapped_backup is not None:
            buggy_path.write_text(swapped_backup, encoding="utf-8")

    return ExecutionResult(task_id=task_dir.name, outcomes=outcomes, line_hits=line_hits)


def _clean(task_dir: Path) -> None:
    """Remove stale bytecode + prior coverage/junit outputs."""
    pycache = task_dir / "__pycache__"
    if pycache.exists():
        for p in pycache.iterdir():
            try:
                p.unlink()
            except OSError:
                pass
    for artifact in (".coverage", "junit.xml"):
        p = task_dir / artifact
        if p.exists():
            p.unlink()
