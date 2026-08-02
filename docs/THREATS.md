# Threats to Validity

Draft list — expand as we run experiments and discover new failure modes.

## Benchmark representativeness

HumanEval methods are short and self-contained. Results here may not
generalize to real-world fault localization on larger codebases with
cross-file dependencies, side effects, or third-party libraries.

## Equivalent mutants

Each mutant is manually inspected and required to fail ≥1 test, which
guards against pure equivalents. But a mutant may still be "semantically
close" — e.g. `<` vs `<=` only diverges on the boundary case, so if
tests don't hit the boundary the fault won't manifest. We include tests
targeting the mutated behavior to reduce this risk.

## Oracle limitations

Ground truth is a single (or small set of) faulty line(s). Some bugs are
non-local — e.g. a wrong constant on line 3 that only causes failure via
line 15. We label the *root cause* line, but the LLM may reasonably point
at a downstream line.

## LLM nondeterminism

Even with `temperature=0`, providers can produce slightly different
outputs across runs (batching, routing, model minor-version drift).
Assignment default is one run per prompt; results are point estimates,
not averages.

## Prompt sensitivity

We use a single fixed prompt design per condition. Different phrasings
could produce meaningfully different results. We do not sweep prompts;
that would multiply the API budget and is out of scope.

## Measurement bias

Line-based scoring can miss the point on multi-statement lines or when
the LLM identifies the region correctly but points at an adjacent line.
The region-accuracy metric partially compensates for this.

## API failures and rate limits

OpenRouter can return transient 429/5xx. We retry with exponential
backoff (`src/llm/openrouter.py`). Persistent failures are logged as
invalid responses and counted toward the invalid-output rate.
