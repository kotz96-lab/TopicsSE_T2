"""Render the static site from data collected via `src.site.collect`
and templates under `site/templates/`.

`build_site()` is the one entry point script/build_site.py calls.
"""

from __future__ import annotations

import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.pipeline.config import DEFAULT_MODELS, load_config
from src.site import collect, plots


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "site" / "templates"
STATIC_DIR = TEMPLATE_DIR / "static"
BUILD_DIR = REPO_ROOT / "site" / "build"


def build_site(*, out_dir: Path | None = None, render_plots: bool = True) -> Path:
    """Collect data + render `templates/index.html.j2` -> `{out}/index.html`.
    Also copies `templates/static/*` and (optionally) generates plots.

    Returns the path to the generated index.html.
    """
    out = out_dir or BUILD_DIR
    out.mkdir(parents=True, exist_ok=True)

    dataset = [asdict(r) for r in collect.collect_dataset()]
    infra = asdict(collect.collect_infra_stats())
    results = collect.collect_results()
    qualitative = [asdict(q) for q in collect.collect_qualitative_examples()]
    env_info = collect.collect_env_info()
    cfg = load_config()

    # Plots — best effort, don't fail the whole build if matplotlib is missing.
    has_plots = False
    plots_dir = out / "plots"
    if render_plots:
        try:
            plots.render_all(results or {}, plots_dir)
            has_plots = True
        except Exception as e:  # noqa: BLE001
            print(f"[warn] plot generation failed: {e}")

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("index.html.j2")
    html = template.render(
        built_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        env=env_info,
        n_tasks=len(dataset),
        n_models=len(cfg.models or DEFAULT_MODELS),
        models=list(cfg.models or DEFAULT_MODELS),
        temperature=cfg.temperature,
        dataset=dataset,
        mutation_counts=collect.mutation_type_counts(collect.collect_dataset()),
        infra=infra,
        results=results,
        qualitative=qualitative,
        has_plots=has_plots,
        docs={
            "threats": collect.collect_doc("THREATS"),
            "ai_tools": collect.collect_doc("AI_TOOLS"),
        },
    )

    index_path = out / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # Copy static assets (CSS).
    static_out = out / "static"
    static_out.mkdir(exist_ok=True)
    for asset in STATIC_DIR.iterdir():
        if asset.is_file():
            shutil.copy2(asset, static_out / asset.name)

    return index_path
