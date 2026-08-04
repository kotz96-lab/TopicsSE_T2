"""Unit tests for the pure helpers in src.testing.runner.

The full `run_with_coverage` is exercised by test_sbfl_integration.py
(slower, spawns pytest as a subprocess).
"""

from pathlib import Path

from src.testing.runner import _normalize_test_id, _parse_junit


class TestNormalizeTestId:
    def test_strips_run_context_suffix(self) -> None:
        ctx = "benchmark/methods/x/test_x.py::test_foo|run"
        assert _normalize_test_id(ctx) == "test_x.py::test_foo"

    def test_strips_setup_context_suffix(self) -> None:
        ctx = "test_x.py::test_foo|setup"
        assert _normalize_test_id(ctx) == "test_x.py::test_foo"

    def test_bare_filename_kept(self) -> None:
        ctx = "test_x.py::test_foo|run"
        assert _normalize_test_id(ctx) == "test_x.py::test_foo"

    def test_non_test_context_returned_verbatim(self) -> None:
        # Empty or module-level context — caller filters these out.
        assert _normalize_test_id("") == ""


class TestParseJunit:
    def _write(self, tmp_path: Path, xml: str) -> Path:
        p = tmp_path / "junit.xml"
        p.write_text(xml, encoding="utf-8")
        return p

    def test_parses_passing_and_failing_cases(self, tmp_path: Path) -> None:
        xml = """<?xml version="1.0"?>
<testsuites>
  <testsuite name="pytest" tests="3">
    <testcase classname="test_x" name="test_a" />
    <testcase classname="test_x" name="test_b">
      <failure message="assert False">traceback...</failure>
    </testcase>
    <testcase classname="test_x" name="test_c" />
  </testsuite>
</testsuites>"""
        outcomes = _parse_junit(self._write(tmp_path, xml))
        assert len(outcomes) == 3
        by_name = {o.test_id: o for o in outcomes}
        assert by_name["test_x.py::test_a"].passed
        assert not by_name["test_x.py::test_b"].passed
        assert by_name["test_x.py::test_b"].error_message.startswith("assert False")
        assert by_name["test_x.py::test_c"].passed

    def test_error_tag_counts_as_failure(self, tmp_path: Path) -> None:
        xml = """<?xml version="1.0"?>
<testsuites>
  <testsuite>
    <testcase classname="test_x" name="test_boom">
      <error message="ZeroDivisionError">stack</error>
    </testcase>
  </testsuite>
</testsuites>"""
        outcomes = _parse_junit(self._write(tmp_path, xml))
        assert len(outcomes) == 1
        assert not outcomes[0].passed
        assert "ZeroDivisionError" in outcomes[0].error_message

    def test_dotted_classname_reduces_to_stem(self, tmp_path: Path) -> None:
        xml = """<?xml version="1.0"?>
<testsuites>
  <testsuite>
    <testcase classname="pkg.subpkg.test_deep" name="test_it" />
  </testsuite>
</testsuites>"""
        outcomes = _parse_junit(self._write(tmp_path, xml))
        assert outcomes[0].test_id == "test_deep.py::test_it"
