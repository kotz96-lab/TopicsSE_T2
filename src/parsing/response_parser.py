"""Parse the structured JSON we asked the LLM to produce.

Expected shape (from the prompt template):

    {
      "top_1_line": 12,
      "top_3_lines": [12, 14, 9],
      "faulty_region": "loop condition",
      "explanation": "..."
    }

Real models sometimes:
  * wrap JSON in ```json fenced code blocks
  * add prose before/after
  * emit integers as strings
  * omit fields

We do a best-effort extraction and return a `ParsedResponse` with an
`is_valid` flag. `is_valid = False` responses still get persisted; they
count toward the required "invalid-output rate" metric.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_BARE_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ParsedResponse:
    is_valid: bool
    top_1_line: int | None = None
    top_3_lines: list[int] = field(default_factory=list)
    faulty_region: str = ""
    explanation: str = ""
    parse_error: str = ""
    raw_json: dict[str, Any] | None = None


def _find_json(text: str) -> str | None:
    m = _FENCED_JSON.search(text)
    if m:
        return m.group(1)
    m = _BARE_OBJECT.search(text)
    return m.group(0) if m else None


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def _coerce_int_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    result: list[int] = []
    for v in value:
        i = _coerce_int(v)
        if i is not None:
            result.append(i)
    return result


def parse(text: str) -> ParsedResponse:
    candidate = _find_json(text)
    if candidate is None:
        return ParsedResponse(is_valid=False, parse_error="no JSON object found in response")
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError as e:
        return ParsedResponse(is_valid=False, parse_error=f"json decode error: {e}")
    if not isinstance(obj, dict):
        return ParsedResponse(is_valid=False, parse_error="top-level JSON is not an object")

    top_1 = _coerce_int(obj.get("top_1_line"))
    top_3 = _coerce_int_list(obj.get("top_3_lines"))
    region = obj.get("faulty_region", "") or ""
    explanation = obj.get("explanation", "") or ""

    # Minimum bar for "valid": we at least got top_1_line as an int.
    is_valid = top_1 is not None
    return ParsedResponse(
        is_valid=is_valid,
        top_1_line=top_1,
        top_3_lines=top_3,
        faulty_region=str(region),
        explanation=str(explanation),
        parse_error="" if is_valid else "missing or invalid top_1_line",
        raw_json=obj,
    )
