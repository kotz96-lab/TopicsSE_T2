"""Prompt building for the four information conditions.

The prompt templates live as text files under `prompts/`. This module loads
them and fills the placeholders so the whole thing is data-driven and easy
to tweak without touching Python.

Template placeholders (Python str.format-style):
  {spec}           natural-language description of intended behavior
  {numbered_code}  buggy code with 1-indexed line numbers prefixed
  {tests_block}    formatted passing/failing test summary (conditions B, D)
  {sbfl_block}     formatted Tarantula ranking (conditions C, D)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


CONDITION_TEMPLATE_FILES: dict[str, str] = {
    "A": "condition_a.txt",
    "B": "condition_b.txt",
    "C": "condition_c.txt",
    "D": "condition_d.txt",
}


@dataclass(frozen=True)
class PromptInputs:
    spec: str
    buggy_source: str
    passing_tests: list[str]      # test IDs
    failing_tests: list[str]      # test IDs; entries may include "expected vs. actual" snippets
    sbfl_ranking: list[tuple[int, float]]  # (line_no, score), pre-sorted desc


def number_lines(source: str) -> str:
    """Prefix each source line with '{n:>4} | ' so the LLM sees exact line
    numbers matching what our ground truth records."""
    lines = source.splitlines()
    width = max(2, len(str(len(lines))))
    return "\n".join(f"{i:>{width}} | {line}" for i, line in enumerate(lines, start=1))


def format_tests_block(inputs: PromptInputs) -> str:
    if not inputs.passing_tests and not inputs.failing_tests:
        return "(no tests provided)"
    lines: list[str] = []
    lines.append(f"Passing tests ({len(inputs.passing_tests)}):")
    for t in inputs.passing_tests:
        lines.append(f"  - {t}")
    lines.append(f"Failing tests ({len(inputs.failing_tests)}):")
    for t in inputs.failing_tests:
        lines.append(f"  - {t}")
    return "\n".join(lines)


def format_sbfl_block(inputs: PromptInputs, top_k: int = 10) -> str:
    if not inputs.sbfl_ranking:
        return "(no SBFL ranking available)"
    top = inputs.sbfl_ranking[:top_k]
    lines = ["Tarantula suspiciousness (higher = more suspicious):"]
    for line_no, score in top:
        lines.append(f"  line {line_no:>3}: {score:.3f}")
    return "\n".join(lines)


def build_prompt(condition: str, inputs: PromptInputs) -> str:
    if condition not in CONDITION_TEMPLATE_FILES:
        raise ValueError(f"Unknown condition {condition!r}; expected one of A/B/C/D")
    template_path = PROMPTS_DIR / CONDITION_TEMPLATE_FILES[condition]
    template = template_path.read_text(encoding="utf-8")
    return template.format(
        spec=inputs.spec.strip(),
        numbered_code=number_lines(inputs.buggy_source),
        tests_block=format_tests_block(inputs),
        sbfl_block=format_sbfl_block(inputs),
    )
