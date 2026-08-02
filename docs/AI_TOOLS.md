# Use of AI-Based Tools

The site's "Use of AI Tools" section will be rendered from this file.
Keep it factual and up to date as we use tools.

## Tools used

- **Claude Code (Anthropic)** — used to help scaffold the repository
  structure, draft prompt templates, and write infrastructure tests. The
  game plan (`docs/GAMEPLAN.md`) was co-written with Claude.

## What we used them for

- Repository skeleton generation (directory layout, .gitignore,
  requirements, pytest/coverage configs).
- Draft prompt templates for the four information conditions.
- Boilerplate for the OpenRouter client + response parser.
- Draft docstrings and inline TODOs.

## How outputs were validated

- All AI-generated infrastructure code (Tarantula formula, response
  parser, metrics) is exercised by pytest tests we wrote by hand.
- Prompt templates were reviewed line-by-line before use in real runs.
- Every LLM-drafted mutation was verified by (a) the original passing all
  tests and (b) the mutant failing ≥1 test. See `scripts/build_dataset.py`.

## Mistakes discovered and corrected

- (Log corrections here as we find them. This is a required part of the
  submission.)
