"""Matplotlib plots for the Results section.

Each function takes the parsed summary JSON (as a dict) and writes a PNG
to `out_dir/`. Kept as small pure functions so they can be swapped or
individually re-generated.
"""

from __future__ import annotations

from pathlib import Path


def _import_plt():
    """Late import so tests / builds without matplotlib installed don't break."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def top1_by_condition(summary: dict, out_dir: Path) -> Path:
    """Grouped bar: Top-1 accuracy per model per condition (A/B/C/D)."""
    plt = _import_plt()
    per_mc = summary.get("by_model_condition", {})
    if not per_mc:
        return _empty(plt, out_dir / "top1_by_condition.png", "Top-1 accuracy by condition")

    conditions = sorted({c for by_c in per_mc.values() for c in by_c})
    models = sorted(per_mc)
    n_models = len(models)
    x = list(range(len(conditions)))
    width = 0.8 / max(n_models, 1)

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
    for i, model in enumerate(models):
        vals = [per_mc[model].get(c, {}).get("top1_accuracy", 0) * 100 for c in conditions]
        offsets = [xi + (i - (n_models - 1) / 2) * width for xi in x]
        ax.bar(offsets, vals, width=width, label=model)

    ax.set_xticks(x)
    ax.set_xticklabels([f"cond {c}" for c in conditions])
    ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Top-1 accuracy by condition")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=8, loc="best")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = out_dir / "top1_by_condition.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def _single_metric_by_condition(summary: dict, out_dir: Path, key: str, title: str,
                                 ylabel: str, filename: str, ylim: tuple[float, float] | None) -> Path:
    plt = _import_plt()
    per_cond = summary.get("by_condition", {})
    if not per_cond:
        return _empty(plt, out_dir / filename, title)

    conditions = sorted(per_cond)
    vals = [per_cond[c].get(key, 0) for c in conditions]
    if key.endswith("accuracy") or key.endswith("rate"):
        vals = [v * 100 for v in vals]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
    ax.bar(range(len(conditions)), vals, color="#1f4287")
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels([f"cond {c}" for c in conditions])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = out_dir / filename
    fig.savefig(path)
    plt.close(fig)
    return path


def mrr_by_condition(summary: dict, out_dir: Path) -> Path:
    return _single_metric_by_condition(
        summary, out_dir, key="mrr",
        title="Mean reciprocal rank by condition",
        ylabel="MRR (0-1)",
        filename="mrr_by_condition.png",
        ylim=(0, 1),
    )


def invalid_by_condition(summary: dict, out_dir: Path) -> Path:
    return _single_metric_by_condition(
        summary, out_dir, key="invalid_rate",
        title="Invalid-output rate by condition",
        ylabel="Invalid rate (%)",
        filename="invalid_by_condition.png",
        ylim=(0, 100),
    )


def _empty(plt, path: Path, title: str) -> Path:
    """Render a 'no data yet' placeholder so the site still has plots."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
    ax.set_title(title)
    ax.text(0.5, 0.5, "no results yet — run the LLM stage",
            ha="center", va="center", transform=ax.transAxes, color="#888")
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def render_all(summary: dict, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return [
        top1_by_condition(summary, out_dir),
        mrr_by_condition(summary, out_dir),
        invalid_by_condition(summary, out_dir),
    ]
