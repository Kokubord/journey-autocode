"""Shared ADR write operations (numbering + file write).

The canonical ADR *schema* lives in :mod:`journey_core.models.adr` (born in feature 004,
ADR-0017 Decision 2). These are the deterministic write OPS that both ``/journey-discover``
(004) and ``/journey-decision`` (012) reuse — a **single source**, no parallel
implementation (anti-drift, eco do ATRITO-61). Writes are routed through the repository
runtime and UNC paths are vetoed (ADR-0004).

The deferred ``/journey-decision`` automation (heuristic duplicate detection, interactive
commit assembly — spec 012 FR-007, não-vivido) is **not** here.
"""

from __future__ import annotations

from pathlib import Path

from journey_core.models.adr import Adr
from journey_core.parsers.adr import parse_adr_index
from journey_core.writer import guard_write_target


def next_adr_number(adr_dir: str | Path) -> int:
    """Return the next free ADR number from the on-disk index (no duplicate)."""
    adrs = parse_adr_index(adr_dir)
    return (adrs[-1].number + 1) if adrs else 1


def write_adr(adr_dir: str | Path, adr: Adr) -> Path:
    """Render ``adr`` to the canonical Markdown and write ``<adr_dir>/<filename>``.

    Args:
        adr_dir: The ``docs/adr/`` directory.
        adr: The ADR to serialize (schema from :mod:`journey_core.models.adr`).

    Returns:
        The written path (vetoes UNC targets — ADR-0004).
    """
    target = guard_write_target(Path(adr_dir) / adr.filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(adr.to_markdown(), encoding="utf-8")
    return target
