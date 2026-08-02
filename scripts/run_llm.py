"""Stage 3 — build prompts for every (task, model, condition) and call
OpenRouter, saving each raw response verbatim.

Reads:
  * benchmark/methods/*     (tasks + ground truth)
  * results/sbfl/*.json     (test outcomes + Tarantula rankings)
  * prompts/condition_*.txt

Writes:
  * results/raw/{task_id}__{model_slug}__{condition}.json
    (the full OpenRouter response body)

Usage:
    python -m scripts.run_llm [--dry-run]

--dry-run only builds prompts (no API calls) — useful for reviewing what
the model will actually see before spending tokens.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Build prompts but do not call the LLM.")
    args = parser.parse_args(argv)

    # TODO(week 3):
    #   1. load .env (python-dotenv)
    #   2. load_config() -> models, temperature, etc.
    #   3. for task in load_all(): for model in models: for cond in CONDITIONS:
    #        prompt = build_prompt(cond, PromptInputs(...))
    #        if not dry_run: response = openrouter.chat(...)
    #        persist raw JSON to results/raw/
    if args.dry_run:
        print("run_llm --dry-run: not implemented yet")
    else:
        print("run_llm: not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
