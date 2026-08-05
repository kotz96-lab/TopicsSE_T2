# Use of AI Tools

## Tools used

- **Claude Code (Anthropic, Opus 4.7 model)** was used as a pair-programming assistant throughout the project. It helped scaffold the repository, write pipeline code, design mutations, and draft documentation and the HTML site.

## What we used it for

### Repository scaffolding
- Directory layout, `.gitignore`, `requirements.txt`, `pytest.ini`, `.coveragerc`.
- Split into stages 1–5 (dataset → SBFL → LLM → metrics → site).

### Dataset construction
- Selected 29 HumanEval tasks (in addition to `HE_000`) spread across 9 mutation categories.
- Designed each mutation to be a single-line change that is caught by at least one HumanEval test or a hand-crafted extra test.
- Generated `original.py`, `buggy.py`, `spec.md`, `meta.json`, and test files via `scripts/scaffold_tasks.py` with the plan in `scripts/task_plan.py`.

### Pipeline code
- `run_with_coverage()` (coverage.py + pytest-cov + JUnit).
- Tarantula and Ochiai formulas + ranking + aggregation.
- OpenRouter client with retry/backoff.
- Prompt-template loading and condition gating.
- Structured-JSON response parsing (with tolerance for fenced code blocks, prose slop, malformed JSON, and API-error stubs).
- Metrics scoring (Top-1, Top-3, region, MRR, invalid rate) and per-model / per-condition aggregation.
- Static HTML site (Jinja2 template + CSS + matplotlib plots).

### Documentation
- Drafts of `docs/GAMEPLAN.md`, `docs/THREATS.md`, and this file.
- README setup and reproduction instructions.
- Site template narrative (RQ descriptions, methodology, threats).

## How outputs were validated

- **Every generated mutant is verified against the two assignment invariants** before it lands in `benchmark/methods/`: `scripts/scaffold_tasks.py` swaps `original.py` into `buggy.py`, runs pytest, restores the mutant, runs pytest again, and rejects the task unless the original passes all tests and the buggy version fails ≥1. This is fully automated.
- **AI-authored infrastructure code is exercised by a hand-designed test suite** (`tests/`) — 89+ pytest tests covering the SBFL formulas, response parser, scoring metrics, mutation helpers, prompt formatting, coverage runner, SBFL aggregator, LLM-condition gating, metrics pipeline, and site collectors + build.
- **Prompt templates were reviewed line-by-line** to make sure condition A really contains no leakage of tests or SBFL info.
- **Real LLM outputs are saved verbatim** to `results/raw/` before any parsing, so any downstream computation can be re-audited without re-hitting the API.

## Mistakes discovered and corrected during the project

- **pytest `-q --no-header` suppresses the summary line**, which broke the initial verifier's regex-based `N passed` count. Fixed by switching to pytest exit codes and ASTs-based test counting.
- **Python `.pyc` cache invalidation compares mtimes at 1-second granularity**, so quickly toggling `buggy.py` ↔ `original.py` in the verifier used stale bytecode. Fixed by passing `-B` to Python and nuking `__pycache__` before each run.
- **`TestOutcome` dataclass was auto-collected as a test class** by pytest because of the `Test` prefix. Silenced via `__test__ = False`.
- **HumanEval task 33 (`sort_third`) has self-referential tests** that compare candidate output to the reference implementation by name — these trivially pass for both buggy and original. Handled by filtering self-referential assertions in the extractor and requiring 10 hand-written tests for this task.
- **JUnit XML files must be forwarded from subprocess-run pytest** because the `-q` output shape changes with TTY detection. Fixed by using `--junitxml` for outcomes and coverage.py's SQLite for line hits.
- **`model_slug()` had to strip forward-slashes and colons** from OpenRouter IDs so they can be used in filenames (`openai/gpt-4o-mini` → `openai__gpt-4o-mini`).
- Several **synthetic test-case expected values were computed incorrectly** during dataset construction (e.g. `fib4(5)` — I had 8 instead of 4). The invariant checker caught these because the original wouldn't pass all tests.
