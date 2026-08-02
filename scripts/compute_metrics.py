"""Stage 4 — parse raw LLM responses and compute the assignment metrics.

Reads:
  * results/raw/*.json         (raw OpenRouter response bodies)
  * benchmark/methods/*/meta.json  (ground-truth faulty lines/region)

Writes:
  * results/parsed/*.json      (cleaned ParsedResponse per call)
  * results/metrics/per_call.csv
  * results/metrics/summary.json  (overall + per-model + per-condition)

Usage:
    python -m scripts.compute_metrics
"""

from __future__ import annotations

import sys


def main() -> int:
    # TODO(week 3): wire src.parsing.response_parser.parse and
    # src.metrics.scoring.summarize, dump CSV + JSON.
    print("compute_metrics: not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
