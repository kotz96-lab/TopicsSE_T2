"""Pure functions that collect data for the static HTML site.

Each function reads files from the repo (dataset, results, docs) and
returns plain Python data suitable for handing to a Jinja2 template.
Kept side-effect-free so the collectors are easy to unit-test with a
temporary directory layout.
"""

from __future__ import annotations

import ast
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------- Dataset ----------------

@dataclass(frozen=True)
class DatasetRow:
    task_id: str
    entry_point: str
    source: str
    mutation_type: str
    faulty_region: str
    faulty_lines: tuple[int, ...]
    mutation_description: str
    n_tests: int
    buggy_snippet: str      # the offending line(s), for the dataset table


def _count_pytest_tests(test_file: Path) -> int:
    tree = ast.parse(test_file.read_text(encoding="utf-8"))
    return sum(
        1 for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def _extract_faulty_snippet(buggy_path: Path, faulty_lines: tuple[int, ...]) -> str:
    if not faulty_lines:
        return ""
    lines = buggy_path.read_text(encoding="utf-8").splitlines()
    snippets = []
    for line_no in faulty_lines:
        if 1 <= line_no <= len(lines):
            snippets.append(lines[line_no - 1].rstrip())
    return "\n".join(snippets)


def collect_dataset(benchmark_root: Path | None = None) -> list[DatasetRow]:
    root = benchmark_root or (REPO_ROOT / "benchmark" / "methods")
    rows: list[DatasetRow] = []
    for task_dir in sorted(root.iterdir()):
        if not task_dir.is_dir():
            continue
        meta_path = task_dir / "meta.json"
        buggy_path = task_dir / "buggy.py"
        if not meta_path.exists() or not buggy_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        test_files = list(task_dir.glob("test_*.py"))
        n_tests = sum(_count_pytest_tests(t) for t in test_files)
        faulty_lines = tuple(meta.get("faulty_lines", []))
        rows.append(DatasetRow(
            task_id=task_dir.name,
            entry_point=meta.get("entry_point", ""),
            source=meta.get("source", ""),
            mutation_type=meta.get("mutation_type", ""),
            faulty_region=meta.get("faulty_region", ""),
            faulty_lines=faulty_lines,
            mutation_description=meta.get("mutation_description", ""),
            n_tests=n_tests,
            buggy_snippet=_extract_faulty_snippet(buggy_path, faulty_lines),
        ))
    return rows


def mutation_type_counts(rows: list[DatasetRow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in rows:
        counts[r.mutation_type] = counts.get(r.mutation_type, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


# ---------------- Infrastructure tests ----------------

@dataclass(frozen=True)
class InfraStats:
    n_tests: int
    n_test_files: int
    coverage_percent: float | None      # None if `coverage.py` hasn't been run
    coverage_by_module: dict[str, float]


def collect_infra_stats(tests_root: Path | None = None) -> InfraStats:
    root = tests_root or (REPO_ROOT / "tests")
    n_files = 0
    n_tests = 0
    for f in root.glob("test_*.py"):
        n_files += 1
        n_tests += _count_pytest_tests(f)

    coverage_percent: float | None = None
    coverage_by_module: dict[str, float] = {}
    cov_json = REPO_ROOT / "coverage.json"
    if cov_json.exists():
        data = json.loads(cov_json.read_text(encoding="utf-8"))
        totals = data.get("totals", {})
        coverage_percent = totals.get("percent_covered")
        for fpath, info in data.get("files", {}).items():
            module = Path(fpath).as_posix()
            summary = info.get("summary", {})
            coverage_by_module[module] = summary.get("percent_covered", 0.0)

    return InfraStats(
        n_tests=n_tests,
        n_test_files=n_files,
        coverage_percent=coverage_percent,
        coverage_by_module=coverage_by_module,
    )


# ---------------- Experimental results ----------------

def collect_results(summary_path: Path | None = None) -> dict:
    """Load results/metrics/summary.json. Returns {} if not present yet
    (e.g. before the first real experiment run)."""
    p = summary_path or (REPO_ROOT / "results" / "metrics" / "summary.json")
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------- Qualitative examples ----------------

@dataclass(frozen=True)
class QualitativeExample:
    task_id: str
    model: str
    condition: str
    faulty_lines: tuple[int, ...]
    top_1_line: int | None
    top_3_lines: tuple[int, ...]
    explanation: str
    kind: str    # human-readable category, e.g. "tests helped", "tarantula misled"


def collect_qualitative_examples(parsed_dir: Path | None = None, limit: int = 5) -> list[QualitativeExample]:
    """Pull a handful of per-call parsed responses that make good
    illustrative examples. Returns [] before any experiment has been run."""
    p = parsed_dir or (REPO_ROOT / "results" / "parsed")
    if not p.exists():
        return []
    examples: list[QualitativeExample] = []
    for f in sorted(p.glob("*.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        if not payload.get("explanation"):
            continue
        examples.append(QualitativeExample(
            task_id=payload.get("task_id", ""),
            model=payload.get("model_slug", ""),
            condition=payload.get("condition", ""),
            faulty_lines=(),
            top_1_line=payload.get("top_1_line"),
            top_3_lines=tuple(payload.get("top_3_lines", [])),
            explanation=payload.get("explanation", ""),
            kind="",
        ))
        if len(examples) >= limit:
            break
    return examples


# ---------------- Reproducibility ----------------

def collect_env_info() -> dict[str, str]:
    """Best-effort Python version + git commit for the reproducibility section."""
    import platform
    info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
        info["git_commit"] = commit
    except (subprocess.CalledProcessError, FileNotFoundError):
        info["git_commit"] = "unknown"
    return info


# ---------------- Markdown pass-through ----------------

def collect_doc(name: str) -> str:
    """Read a docs/*.md file verbatim. Templates render it as pre-wrapped
    text — no markdown-to-HTML dependency needed for the scaffold."""
    p = REPO_ROOT / "docs" / f"{name}.md"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")
