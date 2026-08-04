"""Generate benchmark task folders from HumanEval + a hand-authored mutation plan.

Reads:
    .cache/HumanEval.jsonl        (downloaded once via curl)
    scripts/task_plan.py          (list of TaskSpec dicts, one per bench task)

Writes (per task):
    benchmark/methods/{task_id}/original.py
    benchmark/methods/{task_id}/buggy.py
    benchmark/methods/{task_id}/spec.md
    benchmark/methods/{task_id}/meta.json
    benchmark/methods/{task_id}/test_{entry_point}.py

Also verifies every task before writing meta.json:
    * original.py passes all tests
    * buggy.py fails >= 1 test

Usage:
    python -m scripts.scaffold_tasks              # generate + verify all
    python -m scripts.scaffold_tasks HE_003_below_zero    # single task
    python -m scripts.scaffold_tasks --verify-only        # re-verify existing folders
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
HE_JSONL = REPO_ROOT / ".cache" / "HumanEval.jsonl"
BENCHMARK_ROOT = REPO_ROOT / "benchmark" / "methods"


@dataclass
class TaskSpec:
    """One benchmark entry."""
    task_id: str                    # e.g. 'HE_003_below_zero'
    he_id: str                      # e.g. 'HumanEval/3'
    mutation_type: str              # e.g. 'boundary'
    faulty_region: str              # short label
    mutation_description: str       # human-readable one-liner
    # A pure function that takes the ORIGINAL source (module-level, with
    # `from typing import ...` header etc.) and returns the MUTATED source.
    # It MUST change exactly one line so the ground-truth line is unambiguous.
    mutate: Callable[[str], str]
    # Optional extra test cases beyond what HumanEval provides. Each entry
    # is a Python expression that evaluates to a bool assertion (using
    # `candidate` as the function under test). Example:
    #     "candidate([]) == False"
    # These are appended to the base pytest test file we generate.
    extra_tests: list[str]


# --- HumanEval loading ------------------------------------------------------

def _load_humaneval() -> dict[str, dict]:
    if not HE_JSONL.exists():
        raise SystemExit(
            f"Missing {HE_JSONL}. Download with:\n"
            "  curl -sL https://github.com/openai/human-eval/raw/master/data/"
            "HumanEval.jsonl.gz -o .cache/HumanEval.jsonl.gz && "
            "gzip -df .cache/HumanEval.jsonl.gz"
        )
    with HE_JSONL.open(encoding="utf-8") as f:
        return {json.loads(line)["task_id"]: json.loads(line) for line in f}


# --- Source-code assembly ---------------------------------------------------

def _build_original_source(he_task: dict) -> str:
    """Combine HumanEval's prompt (signature + docstring) with its canonical
    solution to produce a runnable module."""
    return he_task["prompt"] + he_task["canonical_solution"] + "\n"


def _extract_docstring_spec(he_task: dict) -> str:
    """Pull the triple-quoted docstring out of the HumanEval prompt as the
    natural-language spec.md content."""
    mod = ast.parse(he_task["prompt"] + "    pass\n")
    for node in ast.walk(mod):
        if isinstance(node, ast.FunctionDef) and node.name == he_task["entry_point"]:
            doc = ast.get_docstring(node)
            if doc:
                return doc.strip()
    return f"See HumanEval task {he_task['task_id']}."


def _extract_he_test_cases(he_task: dict) -> list[str]:
    """Grab assertions that exercise `candidate` from HumanEval's `test`
    field. Returns each assertion body (i.e. without the leading `assert`).

    We accept both `assert candidate(...) == X` and `assert not candidate(...)`
    style lines. Skip:
      * self-referential tests that call the reference impl by name (e.g.
        `assert tuple(candidate(x)) == tuple(sort_third(x))`) — those would
        trivially pass because our module IS the candidate.
      * `assert True, "..."` debug lines.
    """
    entry_name = he_task["entry_point"]
    lines = []
    for raw in he_task["test"].splitlines():
        stripped = raw.strip()
        if not stripped.startswith("assert "):
            continue
        body = stripped[len("assert "):]
        # Must reference candidate
        if "candidate" not in body:
            continue
        # Skip self-referential ones (e.g. sort_third, HE/33)
        if re.search(rf"\b{re.escape(entry_name)}\b", body):
            continue
        # Skip debug asserts
        if body.startswith("True"):
            continue
        lines.append(body)
    return lines


def _find_line_of_first_diff(original: str, mutated: str) -> int:
    """1-indexed line number of the first line where original != mutated."""
    orig_lines = original.splitlines()
    mut_lines = mutated.splitlines()
    for i, (a, b) in enumerate(zip(orig_lines, mut_lines), start=1):
        if a != b:
            return i
    # One source has extra trailing lines
    return min(len(orig_lines), len(mut_lines)) + 1


# --- File writers -----------------------------------------------------------

_SPEC_TEMPLATE = """# {entry_point}

{docstring}

Source: HumanEval task {he_id}.
"""

def _write_spec(task_dir: Path, he_task: dict, spec_text: str) -> None:
    (task_dir / "spec.md").write_text(
        _SPEC_TEMPLATE.format(
            entry_point=he_task["entry_point"],
            docstring=spec_text,
            he_id=he_task["task_id"],
        ),
        encoding="utf-8",
    )


def _write_test_file(task_dir: Path, he_task: dict, extra_tests: list[str]) -> Path:
    entry = he_task["entry_point"]
    he_assertions = _extract_he_test_cases(he_task)
    lines = [
        f'"""Tests for {entry}. The runner puts this directory on sys.path',
        'and swaps `buggy.py` between the mutant and the original as needed.',
        '"""',
        '',
        f'from buggy import {entry} as candidate  # noqa: E402',
        '',
        '',
    ]
    for i, expr in enumerate(he_assertions, start=1):
        lines.append(f'def test_he_case_{i:02d}():')
        lines.append(f'    assert {expr}')
        lines.append('')
    for i, expr in enumerate(extra_tests, start=1):
        lines.append(f'def test_extra_{i:02d}():')
        lines.append(f'    assert {expr}')
        lines.append('')
    test_path = task_dir / f"test_{entry}.py"
    test_path.write_text("\n".join(lines), encoding="utf-8")
    return test_path


def _write_meta(task_dir: Path, spec: TaskSpec, he_task: dict, faulty_line: int) -> None:
    meta = {
        "task_id": spec.task_id,
        "source": spec.he_id,
        "entry_point": he_task["entry_point"],
        "faulty_lines": [faulty_line],
        "faulty_region": spec.faulty_region,
        "mutation_type": spec.mutation_type,
        "mutation_description": spec.mutation_description,
        "notes": "faulty_lines are 1-indexed against buggy.py.",
    }
    (task_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


# --- Verification -----------------------------------------------------------

def _count_tests(task_dir: Path) -> int:
    """Count top-level `def test_*` functions in the task's test file."""
    entry_test = next(task_dir.glob("test_*.py"))
    tree = ast.parse(entry_test.read_text(encoding="utf-8"))
    return sum(
        1 for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def _run_pytest(task_dir: Path) -> tuple[int, str]:
    """Run pytest against the task's tests. Returns (exit_code, tail_output).
    Exit code 0 = all passed, 1 = one or more failed, 5 = no tests collected.

    NOTE: nukes any `__pycache__` first and passes `-B` to python so we
    don't hit stale bytecode when quickly toggling buggy.py <-> original.py
    (Python's pyc invalidation compares mtimes at 1-second granularity).
    """
    entry_test = next(task_dir.glob("test_*.py"))
    pycache = task_dir / "__pycache__"
    if pycache.exists():
        for p in pycache.iterdir():
            p.unlink()
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", entry_test.name, "-q",
         "-p", "no:cacheprovider", "--tb=short"],
        cwd=str(task_dir), capture_output=True, text=True, timeout=60,
    )
    return proc.returncode, (proc.stdout + proc.stderr)[-800:]


def _verify_task(task_dir: Path) -> tuple[bool, str]:
    """Confirm the two invariants required by the assignment:
      * original passes all tests
      * buggy fails >= 1 test
    Preserves buggy.py contents.
    """
    total = _count_tests(task_dir)
    if total < 10:
        return False, f"only {total} tests in file; need >=10"

    original = (task_dir / "original.py").read_text(encoding="utf-8")
    buggy = (task_dir / "buggy.py").read_text(encoding="utf-8")

    # Test original: exit code MUST be 0.
    (task_dir / "buggy.py").write_text(original, encoding="utf-8")
    try:
        rc_orig, out_orig = _run_pytest(task_dir)
        if rc_orig != 0:
            return False, f"[original.py] pytest exit={rc_orig}\n{out_orig}"
    finally:
        (task_dir / "buggy.py").write_text(buggy, encoding="utf-8")

    # Test buggy: exit code MUST be non-zero (>=1 failure).
    rc_bug, out_bug = _run_pytest(task_dir)
    if rc_bug == 0:
        return False, f"[buggy.py] all tests passed; mutation may be equivalent:\n{out_bug}"

    return True, f"tests={total} | original: all pass | buggy: pytest exit={rc_bug}"


# --- Main -------------------------------------------------------------------

def _generate_one(spec: TaskSpec, he_by_id: dict[str, dict]) -> tuple[bool, str]:
    if spec.he_id not in he_by_id:
        return False, f"unknown HumanEval id {spec.he_id}"
    he_task = he_by_id[spec.he_id]

    original = _build_original_source(he_task)
    buggy = spec.mutate(original)
    if buggy == original:
        return False, "mutate() returned identical source"
    faulty_line = _find_line_of_first_diff(original, buggy)

    task_dir = BENCHMARK_ROOT / spec.task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "original.py").write_text(original, encoding="utf-8")
    (task_dir / "buggy.py").write_text(buggy, encoding="utf-8")
    _write_spec(task_dir, he_task, _extract_docstring_spec(he_task))
    _write_test_file(task_dir, he_task, spec.extra_tests)
    _write_meta(task_dir, spec, he_task, faulty_line)

    ok, msg = _verify_task(task_dir)
    return ok, msg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("only", nargs="?", help="Optional single task_id to (re)generate.")
    parser.add_argument("--verify-only", action="store_true",
                        help="Skip generation; just re-run verification on existing folders.")
    args = parser.parse_args(argv)

    he_by_id = _load_humaneval()

    from scripts.task_plan import TASK_SPECS
    specs = [s for s in TASK_SPECS if not args.only or s.task_id == args.only]
    if not specs:
        print(f"No task matched {args.only!r}. Known tasks:")
        for s in TASK_SPECS:
            print(f"  {s.task_id}")
        return 1

    ok_count = 0
    bad: list[tuple[str, str]] = []
    for spec in specs:
        if args.verify_only:
            task_dir = BENCHMARK_ROOT / spec.task_id
            if not task_dir.exists():
                bad.append((spec.task_id, "folder does not exist"))
                continue
            ok, msg = _verify_task(task_dir)
        else:
            ok, msg = _generate_one(spec, he_by_id)
        marker = "OK  " if ok else "FAIL"
        print(f"[{marker}] {spec.task_id:40s} {msg[:200]}")
        if ok:
            ok_count += 1
        else:
            bad.append((spec.task_id, msg))

    print(f"\n{ok_count}/{len(specs)} tasks passed verification.")
    if bad:
        print("\nFailures:")
        for tid, msg in bad:
            print(f"  {tid}: {msg[:200]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
