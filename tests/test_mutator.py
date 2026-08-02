"""Infrastructure tests for the mutation helpers."""

from src.benchmark.mutator import mutate_first_occurrence, off_by_one_range


class TestMutateFirstOccurrence:
    def test_replaces_only_first_occurrence(self) -> None:
        source = "a = 1\nb = 1\n"
        result = mutate_first_occurrence(source, "1", "2", kind="constant")
        assert result is not None
        assert result.new_source == "a = 2\nb = 1\n"
        assert result.faulty_line == 1

    def test_returns_none_when_pattern_not_found(self) -> None:
        assert mutate_first_occurrence("x = 1\n", "y", "z", kind="constant") is None

    def test_faulty_line_is_1_indexed(self) -> None:
        source = "line1\nline2\ntarget = 1\n"
        result = mutate_first_occurrence(source, "target", "wrong", kind="ident")
        assert result is not None
        assert result.faulty_line == 3


class TestOffByOneRange:
    def test_range_upper_bound_decremented(self) -> None:
        source = "for i in range(10):\n    print(i)\n"
        result = off_by_one_range(source)
        assert result is not None
        assert "range(9)" in result.new_source
        assert result.faulty_line == 1

    def test_returns_none_when_no_range(self) -> None:
        assert off_by_one_range("x = 5\n") is None

    def test_returns_none_when_upper_bound_is_variable(self) -> None:
        # We only mutate integer literals, not names.
        assert off_by_one_range("for i in range(n):\n    pass\n") is None
