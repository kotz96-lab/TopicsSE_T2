"""Load benchmark tasks from `benchmark/methods/`.

Each task directory contains:
  original.py   — reference implementation (passes all tests)
  buggy.py      — mutated version (fails ≥1 test)
  test_*.py     — pytest test file(s), ≥10 tests total
  spec.md       — natural-language spec
  meta.json     — ground truth (see BenchmarkTask.meta)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parents[2] / "benchmark" / "methods"


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    dir: Path
    spec: str
    original_source: str
    buggy_source: str
    meta: dict
    """meta.json shape:
    {
        "faulty_lines": [12],           # 1-indexed line numbers in buggy.py
        "faulty_region": "loop bound",  # short human-readable label
        "mutation_type": "boundary",    # e.g. boundary / operator / off_by_one
        "notes": "..."                  # optional
    }
    """

    @property
    def test_files(self) -> list[Path]:
        return sorted(self.dir.glob("test_*.py"))


def load_task(task_dir: Path) -> BenchmarkTask:
    spec = (task_dir / "spec.md").read_text(encoding="utf-8")
    original = (task_dir / "original.py").read_text(encoding="utf-8")
    buggy = (task_dir / "buggy.py").read_text(encoding="utf-8")
    meta = json.loads((task_dir / "meta.json").read_text(encoding="utf-8"))
    return BenchmarkTask(
        task_id=task_dir.name,
        dir=task_dir,
        spec=spec,
        original_source=original,
        buggy_source=buggy,
        meta=meta,
    )


def load_all(root: Path = BENCHMARK_ROOT) -> list[BenchmarkTask]:
    return [load_task(d) for d in sorted(root.iterdir()) if d.is_dir()]
