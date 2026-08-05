"""Stage 5 — build the static HTML site.

Reads:
    benchmark/methods/*/meta.json    — dataset table
    tests/*                          — infra test count
    results/metrics/summary.json     — headline + result tables (optional)
    results/parsed/*.json            — qualitative examples (optional)
    docs/THREATS.md, docs/AI_TOOLS.md — verbatim section content

Writes:
    site/build/index.html
    site/build/static/style.css
    site/build/plots/*.png

Usage:
    python -m scripts.build_site                # rebuild everything
    python -m scripts.build_site --no-plots     # skip matplotlib (faster)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.site.generate import build_site   # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plots", action="store_true",
                        help="Skip plot generation (matplotlib not required).")
    args = parser.parse_args(argv)
    index_path = build_site(render_plots=not args.no_plots)
    print(f"Wrote {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
