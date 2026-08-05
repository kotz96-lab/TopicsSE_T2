"""Unit tests for the site collectors + integration test for the site build.

These use isolated temp directories where possible so they don't depend on
transient repo state (e.g. whether results/metrics/summary.json exists).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.site import collect, generate


class TestCollectDataset:
    def test_reads_real_benchmark(self) -> None:
        rows = collect.collect_dataset()
        assert len(rows) >= 30, "expected at least 30 benchmark tasks"
        by_id = {r.task_id: r for r in rows}
        assert "HE_000_has_close_elements" in by_id
        row = by_id["HE_000_has_close_elements"]
        assert row.n_tests >= 10
        assert row.faulty_lines == (6,)
        assert row.mutation_type == "boundary"

    def test_all_rows_have_a_faulty_line(self) -> None:
        for row in collect.collect_dataset():
            assert row.faulty_lines, f"{row.task_id} missing faulty_lines"

    def test_snippet_extracted_from_buggy_source(self) -> None:
        by_id = {r.task_id: r for r in collect.collect_dataset()}
        row = by_id["HE_000_has_close_elements"]
        # Buggy line for HE_000 is `if distance <= threshold:` — snippet
        # must contain the mutated operator.
        assert "<= threshold" in row.buggy_snippet


class TestMutationCounts:
    def test_all_categories_present(self) -> None:
        rows = collect.collect_dataset()
        counts = collect.mutation_type_counts(rows)
        # Should have several distinct mutation types.
        assert len(counts) >= 5


class TestCollectResults:
    def test_missing_summary_returns_empty(self, tmp_path: Path) -> None:
        assert collect.collect_results(tmp_path / "nope.json") == {}

    def test_reads_summary_json(self, tmp_path: Path) -> None:
        p = tmp_path / "summary.json"
        p.write_text(json.dumps({"overall": {"top1_accuracy": 0.42}}), encoding="utf-8")
        assert collect.collect_results(p)["overall"]["top1_accuracy"] == 0.42


class TestCollectInfraStats:
    def test_counts_test_functions(self, tmp_path: Path) -> None:
        (tmp_path / "test_a.py").write_text(
            "def test_one():\n    pass\ndef test_two():\n    pass\n", encoding="utf-8"
        )
        (tmp_path / "test_b.py").write_text(
            "def test_x():\n    pass\n", encoding="utf-8"
        )
        stats = collect.collect_infra_stats(tmp_path)
        assert stats.n_test_files == 2
        assert stats.n_tests == 3


class TestCollectDoc:
    def test_missing_doc_returns_empty(self) -> None:
        assert collect.collect_doc("does_not_exist") == ""

    def test_reads_docs_folder(self) -> None:
        # THREATS.md and AI_TOOLS.md were added in the initial scaffold.
        text = collect.collect_doc("THREATS")
        assert "Threats to Validity" in text or "threat" in text.lower()


class TestBuildSite:
    def test_build_renders_html_with_all_required_sections(self, tmp_path: Path) -> None:
        # `--no-plots` equivalent so we don't require matplotlib in this test.
        index = generate.build_site(out_dir=tmp_path, render_plots=False)
        assert index.exists()
        html = index.read_text(encoding="utf-8")
        for section_id in ("overview", "dataset", "design", "validation",
                            "results", "qualitative", "threats",
                            "reproducibility", "ai-tools"):
            assert f'id="{section_id}"' in html, f"missing section: {section_id}"

    def test_build_copies_stylesheet(self, tmp_path: Path) -> None:
        generate.build_site(out_dir=tmp_path, render_plots=False)
        assert (tmp_path / "static" / "style.css").exists()

    def test_build_survives_no_results(self, tmp_path: Path, monkeypatch) -> None:
        # Point results-collection at a directory with no summary.json.
        monkeypatch.setattr(collect, "collect_results", lambda *a, **kw: {})
        monkeypatch.setattr(collect, "collect_qualitative_examples", lambda *a, **kw: [])
        index = generate.build_site(out_dir=tmp_path, render_plots=False)
        html = index.read_text(encoding="utf-8")
        # Falls back to the informative callout.
        assert "no-api" not in html.lower()  # sanity: no dev-note leaking
        assert "callout" in html
        # No results-table headers when there are no results.
        assert "By information condition" not in html
