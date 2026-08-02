# results/

Everything the pipeline writes lands here. Layout:

```
results/
├── sbfl/                # per-task Tarantula rankings and coverage aggregation
│   └── {task_id}.json
├── raw/                 # raw LLM responses (JSON body from OpenRouter)
│   └── {task_id}__{model_slug}__{condition}.json
├── parsed/              # cleaned + validated model outputs
│   └── {task_id}__{model_slug}__{condition}.json
├── coverage/            # coverage.py data files (per-test contexts)
│   └── {task_id}.coverage
├── metrics/
│   ├── per_call.csv     # one row per (task, model, condition)
│   └── summary.json     # aggregated Top-1 / Top-3 / MRR / invalid rate
└── plots/               # PNG plots consumed by the HTML site
```

The `raw/`, `parsed/`, `sbfl/`, `coverage/` directories are gitignored. Only
`metrics/` and `plots/` should be committed when we want to snapshot published
results (do this manually with `git add -f`).
