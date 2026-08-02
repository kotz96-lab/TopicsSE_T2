"""Minimal OpenRouter chat-completions client.

Design notes:
  * Uses `requests` (kept synchronous — 240 calls is fine sequentially).
  * Reads `OPENROUTER_API_KEY` from env (via python-dotenv in the CLI script).
  * Sets `HTTP-Referer` and `X-Title` headers that OpenRouter recommends.
  * Retries with exponential backoff on transient errors (429/5xx).
  * Returns the full JSON body so raw responses can be persisted verbatim.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass(frozen=True)
class OpenRouterCall:
    model: str
    prompt: str
    temperature: float = 0.0
    max_tokens: int = 1024


class OpenRouterError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("OPENROUTER_API_KEY not set in environment")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", ""),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "TopicsSE_T2"),
    }


def chat(call: OpenRouterCall, *, max_retries: int = 4, timeout: float = 60.0) -> dict[str, Any]:
    """Send a single chat-completions request. Returns the full JSON body."""
    payload = {
        "model": call.model,
        "messages": [{"role": "user", "content": call.prompt}],
        "temperature": call.temperature,
        "max_tokens": call.max_tokens,
    }
    backoff = 1.5
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                OPENROUTER_URL, headers=_headers(), json=payload, timeout=timeout
            )
            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                last_err = OpenRouterError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(backoff ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            last_err = e
            time.sleep(backoff ** attempt)
    raise OpenRouterError(f"OpenRouter call failed after {max_retries} attempts: {last_err}")


def extract_text(response_json: dict[str, Any]) -> str:
    """Pull the assistant message text out of an OpenRouter response body."""
    try:
        return response_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise OpenRouterError(f"Malformed OpenRouter response: {e}") from e
