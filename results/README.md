# results/

Everything the pipeline writes lands here. Layout:

```
results/
├── sbfl/                # per-task Tarantula rankings and coverage aggregation
│   └── {task_id}.json                       — written by scripts/run_sbfl.py
├── prompts/             # every prompt built by scripts/run_llm.py
│   └── {task_id}__{model_slug}__cond{X}.txt
├── raw/                 # raw LLM responses (full OpenRouter body OR error stub)
│   └── {task_id}__{model_slug}__cond{X}.json
├── parsed/              # cleaned model predictions
│   └── {task_id}__{model_slug}__cond{X}.json
├── coverage/            # coverage.py data files (per-test contexts, per task)
│   ├── {task_id}.coverage
│   └── {task_id}.junit.xml
├── metrics/
│   ├── per_call.csv     # one row per (task, model, condition)
│   └── summary.json     # nested: overall / by_model / by_condition / by_model_condition
└── plots/               # PNG plots consumed by the HTML site (week 4)
```

Everything under `results/` is gitignored by default so intermediate work
doesn't pollute the repo. When we're ready to snapshot published numbers
for the site, force-add manually:

```bash
git add -f results/metrics/summary.json results/plots/*.png
```
