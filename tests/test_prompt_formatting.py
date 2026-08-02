"""Infrastructure tests for prompt template loading and formatting.

These tests use the real template files under prompts/ — that way if a
template file is deleted or its placeholders are renamed the tests catch it.
"""

import pytest

from src.llm.prompts import (
    PromptInputs,
    build_prompt,
    format_sbfl_block,
    format_tests_block,
    number_lines,
)


class TestNumberLines:
    def test_line_numbering_is_1_indexed(self) -> None:
        numbered = number_lines("a\nb\nc")
        assert numbered.splitlines()[0].startswith(" 1 |")
        assert numbered.splitlines()[2].startswith(" 3 |")

    def test_wider_files_use_wider_number_column(self) -> None:
        source = "\n".join(["x"] * 12)
        numbered = number_lines(source)
        # 12-line file needs 2-char-wide numbering
        assert numbered.splitlines()[0].startswith(" 1 |")
        assert numbered.splitlines()[11].startswith("12 |")


class TestFormatBlocks:
    def test_tests_block_shows_pass_fail_counts(self) -> None:
        inputs = PromptInputs(
            spec="", buggy_source="",
            passing_tests=["t1", "t2"],
            failing_tests=["t3"],
            sbfl_ranking=[],
        )
        block = format_tests_block(inputs)
        assert "Passing tests (2)" in block
        assert "Failing tests (1)" in block
        assert "- t3" in block

    def test_empty_tests_block_is_labeled(self) -> None:
        inputs = PromptInputs("", "", [], [], [])
        assert format_tests_block(inputs) == "(no tests provided)"

    def test_sbfl_block_truncates_to_top_k(self) -> None:
        ranking = [(i, 1.0 - i * 0.1) for i in range(1, 21)]
        inputs = PromptInputs("", "", [], [], ranking)
        block = format_sbfl_block(inputs, top_k=5)
        # One "line N: score" row per ranked entry.
        assert block.count("\n  line") == 5


class TestBuildPrompt:
    @pytest.mark.parametrize("condition", ["A", "B", "C", "D"])
    def test_each_condition_renders_without_error(self, condition: str) -> None:
        inputs = PromptInputs(
            spec="Return the sum of two ints.",
            buggy_source="def add(a, b):\n    return a - b\n",
            passing_tests=["test_zero"],
            failing_tests=["test_positive"],
            sbfl_ranking=[(2, 1.0), (1, 0.0)],
        )
        prompt = build_prompt(condition, inputs)
        assert "Return the sum of two ints." in prompt
        assert "a - b" in prompt
        # JSON schema instruction is present regardless of condition
        assert "top_1_line" in prompt

    def test_unknown_condition_raises(self) -> None:
        inputs = PromptInputs("", "def f(): pass\n", [], [], [])
        with pytest.raises(ValueError):
            build_prompt("Z", inputs)

    def test_condition_a_does_not_leak_test_or_sbfl_labels(self) -> None:
        inputs = PromptInputs(
            spec="s", buggy_source="def f(): pass\n",
            passing_tests=["p"], failing_tests=["f"],
            sbfl_ranking=[(1, 1.0)],
        )
        prompt = build_prompt("A", inputs)
        # A must not mention Tarantula / test results sections.
        assert "Tarantula ranking" not in prompt
        assert "Test results" not in prompt
