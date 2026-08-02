# TopicsSE_T2 — LLMs for Fault Localization

Empirical study comparing how well LLMs localize faults in buggy Python methods
under four information conditions (code only / +tests / +SBFL / +tests+SBFL),
across at least two models via OpenRouter.

Course: **Topics in Software Engineering** — Assignment 2.

> New here? Read [`docs/GAMEPLAN.md`](docs/GAMEPLAN.md) first — it explains
> the whole thing in plain English.

## Setup

```bash
# 1. Clone
git clone git@github.com:kotz96-lab/TopicsSE_T2.git
cd TopicsSE_T2

# 2. Virtualenv + deps
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt

# 3. API key
cp .env.example .env
# then edit .env and paste your OPENROUTER_API_KEY
```

## Repo layout

```
.
├── benchmark/              # dataset: one folder per problem
│   └── methods/{task_id}/
│       ├── original.py     # reference (passing) implementation
│       ├── buggy.py        # mutated version (the one under study)
│       ├── test_*.py       # ≥10 tests
│       ├── spec.md         # natural-language spec
│       └── meta.json       # ground truth: faulty line(s), mutation type
├── src/                    # experiment library
│   ├── benchmark/          # dataset loading, mutation helpers
│   ├── testing/            # test runner + coverage capture
│   ├── sbfl/               # Tarantula + other formulas
│   ├── llm/                # OpenRouter client + prompt builders
│   ├── parsing/            # parse structured JSON responses
│   ├── metrics/            # Top-1, Top-3, MRR, region acc, invalid rate
│   ├── pipeline/           # end-to-end orchestration
│   └── site/               # static HTML generation
├── scripts/                # thin CLI wrappers over src/
│   ├── build_dataset.py
│   ├── run_sbfl.py
│   ├── run_llm.py
│   ├── compute_metrics.py
│   └── build_site.py
├── prompts/                # A/B/C/D prompt templates
├── tests/                  # our own infrastructure tests (pytest)
├── results/                # pipeline outputs (mostly gitignored)
├── site/                   # generated static HTML
└── docs/                   # planning + notes
```

## How to run the pipeline

Each stage is independently re-runnable. Outputs of one feed the next.

```bash
# Stage 1 — validate dataset (original passes, buggy fails ≥1 test)
python -m scripts.build_dataset

# Stage 2 — run tests with coverage, compute Tarantula rankings
python -m scripts.run_sbfl

# Stage 3 — build prompts + call OpenRouter (needs .env)
python -m scripts.run_llm

# Stage 4 — parse responses, compute metrics
python -m scripts.compute_metrics

# Stage 5 — generate the static HTML report
python -m scripts.build_site
```

Open `site/build/index.html` in a browser to view the report.

## Running our own tests (infrastructure validation)

```bash
pytest                                    # run all infra tests
pytest --cov=src --cov-report=html        # with coverage report
```

Coverage HTML lands in `htmlcov/index.html`.

## Reproducibility notes

- **Python:** 3.11+ (developed on 3.11 / 3.12).
- **Determinism:** LLM calls use `temperature=0` and one repetition per prompt
  (per the assignment default). LLM output is still not perfectly
  deterministic — see the *Threats to Validity* section in the site.
- **Costs:** ~240 LLM calls per full run. Choose cheap models on OpenRouter.

## What's *not* in this repo

- **API keys.** Never commit `.env`. See `.env.example` for the shape.
- **Bulk raw outputs.** `results/raw/` is gitignored; regenerate with
  `scripts/run_llm.py`. Aggregated metrics + plots get committed manually.

## Assignment mapping

| Requirement                          | Where it lives                       |
| ------------------------------------ | ------------------------------------ |
| Dataset + mutants                    | `benchmark/methods/`                 |
| SBFL / Tarantula                     | `src/sbfl/`, `scripts/run_sbfl.py`   |
| OpenRouter integration               | `src/llm/openrouter.py`              |
| Prompt templates (4 conditions)      | `prompts/condition_{a,b,c,d}.txt`    |
| Metrics (Top-1/3, MRR, region, invalid rate) | `src/metrics/scoring.py`     |
| Infrastructure tests                 | `tests/`                             |
| Static HTML site                     | `src/site/`, `site/build/index.html` |
| AI-tool usage discussion             | `docs/AI_TOOLS.md` (to be added)     |
| Threats to validity                  | `docs/THREATS.md` (to be added)      |
