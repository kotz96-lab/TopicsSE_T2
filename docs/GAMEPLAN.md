# Game Plan — LLMs for Fault Localization

Human-speak walkthrough of what we're building and how the pieces fit together.

## What the assignment actually asks

We're running a science experiment on LLMs. Question: **how good are LLMs at pointing at the buggy line in a Python method, and does giving them extra hints (tests, SBFL rankings) actually help?**

Concretely:
1. Grab ~30 small Python functions (HumanEval-style — short specs, easy to test).
2. Break each one on purpose (mutation) so we know exactly which line is bad.
3. Run the tests, record which pass/fail and which lines each test touches.
4. From the coverage data, compute a **Tarantula** suspicion score per line.
5. Ask two LLMs (via OpenRouter) to find the bug in four different setups:
   - **A** = code only
   - **B** = code + tests
   - **C** = code + Tarantula ranking
   - **D** = code + tests + Tarantula ranking
6. Score their answers (Top-1, Top-3, MRR, region-hit, invalid-output rate).
7. Write our own pytest tests for the experiment code so we know the results aren't garbage.
8. Wrap it all in a static HTML site + a 5–10 min video.

That's `30 methods × 2 models × 4 conditions = 240` LLM calls minimum.

## The five research questions in plain English

- **RQ1** — Can an LLM find bugs cold, with just the code and the spec?
- **RQ2** — Do tests help?
- **RQ3** — Does a Tarantula ranking help?
- **RQ4** — Does giving it both help more than either alone?
- **RQ5** — Are some models just better at this than others?

## Architecture (mental model)

Think of it as a pipeline with stages, each writing files that the next stage reads:

```
benchmark/ (methods, mutants, specs, tests)
        │
        ▼
run tests + coverage  ──►  results/sbfl/{task}.json  (pass/fail sets, tarantula scores)
        │
        ▼
build prompt (A/B/C/D)  ──►  prompts/{task}_{model}_{cond}.txt
        │
        ▼
OpenRouter call  ──►  results/raw/{task}_{model}_{cond}.json  (raw model response)
        │
        ▼
parse JSON  ──►  results/parsed/{task}_{model}_{cond}.json
        │
        ▼
score vs. ground truth  ──►  results/metrics/summary.json
        │
        ▼
build_site.py  ──►  site/index.html
```

Every stage is a plain script under `scripts/` calling library code under `src/`. That way each stage is independently re-runnable and testable.

## What lives where

- **`benchmark/methods/{task_id}/`** — one folder per problem, contains `original.py`, `buggy.py`, `test_*.py`, `spec.md`, `meta.json` (which line is the bug, what mutation was applied, etc.).
- **`src/`** — the actual experiment library. Small focused modules so we can unit test them.
- **`scripts/`** — thin CLI wrappers that stitch the library into pipeline stages.
- **`tests/`** — **our own** infrastructure tests (this is the "validate your infrastructure" bit — worth 15 points).
- **`prompts/`** — the four prompt templates (A/B/C/D).
- **`results/`** — everything the pipeline writes. Raw outputs stay so we can re-score without re-paying for API calls.
- **`site/`** — generated static HTML.
- **`docs/`** — planning docs, this file, notes on threats to validity, AI-tool usage.

## Weekly rough plan (matches the assignment's milestones)

**Week 1 — Foundations** ✅
- Repo skeleton, README, requirements, .gitignore.
- One example HumanEval method wired end-to-end.
- `pytest` setup + first infrastructure tests.
- Mutation plan sketched out.
- Prompt templates drafted for all four conditions.

**Week 2 — Dataset + SBFL** ✅
- 30 HumanEval-based tasks under `benchmark/methods/`, ≥10 tests each.
- One mutation per method, spread across 9 categories.
- `scripts/scaffold_tasks.py` enforces the two invariants (original passes all, buggy fails ≥1).
- `src/testing/runner.py` + `scripts/run_sbfl.py` — coverage-based per-test spectra + Tarantula/Ochiai rankings.
- Baseline: Tarantula alone hits Top-1 30%, Top-3 83%, MRR 0.559.

**Week 3 — LLM runs** ✅
- Two free models via OpenRouter (`openai/gpt-oss-20b:free` and `google/gemma-4-31b-it:free`).
- `scripts/run_llm.py` covers all 30 × 2 × 4 = 240 combinations, `--dry-run` for prompt inspection.
- `scripts/compute_metrics.py` produces per-call CSV + nested summary JSON.
- Condition gating (A/B/C/D) enforced and unit-tested.

**Week 4 — Site + polish**
- Static HTML site (`scripts/build_site.py` → `site/build/index.html`) — Jinja2 template + matplotlib plots + all 9 required sections.
- Cross-condition qualitative-example picker (tests helped / SBFL helped / SBFL misled / plausible-but-wrong / combined helped).
- Remaining polish: video script, final review pass.

## Key design decisions worth flagging early

1. **One mutation per method, kept simple.** The assignment allows more sophisticated stuff but starts to bite when we have to verify "not equivalent" and "reasonably localizable". Sticking to boundary / operator / off-by-one style mutations keeps ground truth cleanly defined.

2. **Line-level coverage using `coverage.py`.** It ships with `--data-file` per-test tracking via contexts (`--cov-context=test`). Cleaner than rolling our own tracer.

3. **Fixed prompt template, structured JSON output.** The assignment explicitly wants this. Ask model to return `{"top_1_line": int, "top_3_lines": [ints], "faulty_region": str, "explanation": str}`. When parsing fails → count as invalid output (that's a required metric).

4. **Save everything raw.** Every LLM response goes to disk before parsing so re-scoring is free and reproducible.

5. **Temperature = 0** for reproducibility. One run per prompt per the default.

6. **No API keys in the repo.** `.env.example` shows the shape; real key goes in `.env` which is gitignored.

## Risks / things to watch

- **OpenRouter rate limits** on cheap models — add retry/backoff, log every failure.
- **Equivalent mutants** — need to eyeball each mutant to make sure it's actually semantically different.
- **Coverage on tiny methods** — some HumanEval functions are 3 lines long. Ranking is trivial in those cases; may want to lean toward slightly longer ones.
- **Prompt sensitivity** — the assignment names this as a threat to validity. We only run one prompt design; we should acknowledge that in the write-up, not try to sweep it.
- **Test count per method** — assignment says ≥10 per method. HumanEval usually ships with 5–8; we'll need to write extras. Budget time for this.

## Definition of "done" for the scaffolding pass

- Repo cloneable, `pip install -r requirements.txt` works.
- `pytest` runs (even if only trivial tests pass).
- One example method in `benchmark/methods/` shows the intended folder shape.
- All the module stubs exist so real code can drop in without moving things around.
- README explains how to run each stage.
