"""Stage 5 — assemble the static HTML report from results/.

Reads:
  * results/metrics/summary.json
  * results/plots/*.png
  * results/parsed/*.json  (qualitative examples)

Writes:
  * site/build/index.html   (and any supporting CSS/JS/images)

Usage:
    python -m scripts.build_site
"""

from __future__ import annotations

import sys


def main() -> int:
    # TODO(week 4): read result JSON, render Jinja2 templates from
    # site/templates/ to site/build/.
    print("build_site: not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
