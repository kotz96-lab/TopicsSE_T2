"""Central experiment configuration.

Kept as a plain module (not JSON/YAML) so IDEs give completion and it's
grep-friendly. Everything here is intentionally overridable via env vars
for CI / reproducibility runs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "benchmark" / "methods"
RESULTS_ROOT = REPO_ROOT / "results"
PROMPTS_ROOT = REPO_ROOT / "prompts"
SITE_ROOT = REPO_ROOT / "site"


DEFAULT_MODELS: tuple[str, ...] = (
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
)

CONDITIONS: tuple[str, ...] = ("A", "B", "C", "D")


@dataclass(frozen=True)
class ExperimentConfig:
    models: tuple[str, ...]
    conditions: tuple[str, ...]
    temperature: float
    max_tokens: int
    repetitions: int


def load_config() -> ExperimentConfig:
    env_models = os.environ.get("LLM_MODELS")
    models = tuple(m.strip() for m in env_models.split(",")) if env_models else DEFAULT_MODELS
    return ExperimentConfig(
        models=models,
        conditions=CONDITIONS,
        temperature=float(os.environ.get("LLM_TEMPERATURE", "0.0")),
        max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "1024")),
        repetitions=int(os.environ.get("LLM_REPETITIONS", "1")),
    )


def model_slug(model_id: str) -> str:
    """Safe filesystem slug for a model ID like 'openai/gpt-4o-mini'."""
    return model_id.replace("/", "__").replace(":", "_")
