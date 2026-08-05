"""Tests for the condition-gating logic in scripts/run_llm.

The key invariant we need to enforce: condition A gets NO test outcomes
and NO Tarantula ranking; B gets tests only; C gets Tarantula only; D
gets both. If this leaks, the whole experiment is invalid.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts.run_llm import _build_inputs_for, _out_name


# Any real benchmark task with an SBFL report already computed works here.
CANDIDATE_TASKS = [
    REPO_ROOT / "benchmark" / "methods" / "HE_000_has_close_elements",
    REPO_ROOT / "benchmark" / "methods" / "HE_003_below_zero",
]


@pytest.fixture(scope="module")
def task_with_sbfl():
    for d in CANDIDATE_TASKS:
        sbfl_path = REPO_ROOT / "results" / "sbfl" / f"{d.name}.json"
        if d.exists() and sbfl_path.exists():
            return d
    pytest.skip("No benchmark task with SBFL report available")


class TestConditionGating:
    def test_condition_A_has_no_tests_and_no_sbfl(self, task_with_sbfl) -> None:
        inputs = _build_inputs_for(task_with_sbfl, "A")
        assert inputs.passing_tests == []
        assert inputs.failing_tests == []
        assert inputs.sbfl_ranking == []

    def test_condition_B_has_tests_but_no_sbfl(self, task_with_sbfl) -> None:
        inputs = _build_inputs_for(task_with_sbfl, "B")
        assert inputs.passing_tests or inputs.failing_tests, "should include some tests"
        assert inputs.sbfl_ranking == []

    def test_condition_C_has_sbfl_but_no_tests(self, task_with_sbfl) -> None:
        inputs = _build_inputs_for(task_with_sbfl, "C")
        assert inputs.passing_tests == []
        assert inputs.failing_tests == []
        assert inputs.sbfl_ranking, "should include SBFL ranking"

    def test_condition_D_has_both(self, task_with_sbfl) -> None:
        inputs = _build_inputs_for(task_with_sbfl, "D")
        assert inputs.passing_tests or inputs.failing_tests
        assert inputs.sbfl_ranking

    def test_all_conditions_carry_spec_and_code(self, task_with_sbfl) -> None:
        for cond in ("A", "B", "C", "D"):
            inputs = _build_inputs_for(task_with_sbfl, cond)
            assert inputs.spec, f"spec missing for condition {cond}"
            assert inputs.buggy_source, f"code missing for condition {cond}"

    def test_unknown_condition_raises(self, task_with_sbfl) -> None:
        with pytest.raises(ValueError):
            _build_inputs_for(task_with_sbfl, "Z")


class TestOutFileNaming:
    def test_filename_has_task_model_condition(self) -> None:
        name = _out_name("HE_003_below_zero", "openai/gpt-4o-mini", "B", "json")
        assert name.startswith("HE_003_below_zero__")
        assert "openai__gpt-4o-mini" in name
        assert name.endswith("__condB.json")

    def test_slashes_and_colons_in_model_id_escaped(self) -> None:
        # Filesystem-hostile characters must not appear in the output name.
        name = _out_name("t", "vendor/family:sub", "A", "txt")
        assert "/" not in name
        assert ":" not in name
