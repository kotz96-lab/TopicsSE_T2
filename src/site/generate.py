"""Assemble the static HTML report from templates + result JSON.

Sections match the assignment's Section 8 requirements:
  Overview / Dataset / Experimental Design / Validation of Infrastructure /
  Results / Qualitative Analysis / Threats to Validity / Reproducibility /
  Use of AI Tools.

Templates live under `site/templates/` and are rendered with Jinja2.
Output goes to `site/build/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "site" / "templates"
BUILD_DIR = Path(__file__).resolve().parents[2] / "site" / "build"


@dataclass
class SiteContext:
    overview: dict[str, Any]
    dataset: dict[str, Any]
    experimental_design: dict[str, Any]
    validation: dict[str, Any]
    results: dict[str, Any]
    qualitative: dict[str, Any]
    threats: dict[str, Any]
    reproducibility: dict[str, Any]
    ai_tools: dict[str, Any]


def render_site(ctx: SiteContext, *, out_dir: Path = BUILD_DIR) -> Path:
    """Render `templates/index.html.j2` -> `out_dir/index.html`.

    TODO(week 4): fill in — for now just makes sure the directory exists
    and returns the target path so scripts can wire the flow.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "index.html"
    # Actual Jinja2 rendering added in week 4.
    return target
