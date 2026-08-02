"""Small helpers for producing buggy variants of a method by textual mutation.

We keep mutations *simple and localized* on purpose — the ground-truth line
must remain obvious and the mutant must not be equivalent to the original.

Every mutator returns (new_source, faulty_line_1indexed) so we can immediately
write the ground truth to `meta.json`.

TODO(week 2): expand catalogue and add a `validate_mutant()` that runs the
tests to confirm original passes and mutant fails ≥1.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MutationResult:
    new_source: str
    faulty_line: int
    mutation_type: str
    description: str


_BINARY_OPS: dict[str, str] = {
    "<=": "<",
    ">=": ">",
    "==": "!=",
    "+": "-",
    "-": "+",
    "*": "/",
    " and ": " or ",
    " or ": " and ",
}


def mutate_first_occurrence(source: str, old: str, new: str, kind: str) -> MutationResult | None:
    """Replace the first `old` with `new`. Returns None if `old` not found."""
    idx = source.find(old)
    if idx < 0:
        return None
    line_no = source.count("\n", 0, idx) + 1
    new_source = source[:idx] + new + source[idx + len(old):]
    return MutationResult(
        new_source=new_source,
        faulty_line=line_no,
        mutation_type=kind,
        description=f"replaced first occurrence of '{old.strip()}' with '{new.strip()}'",
    )


def off_by_one_range(source: str) -> MutationResult | None:
    """Change the first `range(..., X)` upper bound `X` -> `X - 1`.

    Only handles integer literals; more general expressions are out of scope.
    """
    match = re.search(r"range\((?P<inner>[^)]+)\)", source)
    if not match:
        return None
    inner = match.group("inner")
    parts = [p.strip() for p in inner.split(",")]
    if not parts or not parts[-1].isdigit():
        return None
    new_stop = str(int(parts[-1]) - 1)
    parts[-1] = new_stop
    new_inner = ", ".join(parts)
    start, end = match.span()
    new_source = source[:start] + f"range({new_inner})" + source[end:]
    line_no = source.count("\n", 0, start) + 1
    return MutationResult(
        new_source=new_source,
        faulty_line=line_no,
        mutation_type="off_by_one",
        description=f"decremented range stop {match.group('inner')} -> {new_inner}",
    )
