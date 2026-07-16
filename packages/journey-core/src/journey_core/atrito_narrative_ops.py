"""Authoring op for the didactic ATRITO narratives (ADR-0046, Build-2).

The didactic narrative of an ATRITO (plain-language prose for the non-dev ICP) is authored in
the IDE and persisted to ``docs/atrito-narratives.yaml`` (keyed by ATRITO ref). The Site reads
it ON-DEMAND (decision route) and never gains an LLM (fronteira ADR-0032). This module is the
single write source the nourish skill reuses, mirroring :mod:`journey_core.briefing_ops` (same
yaml load/dump + ``guard_write_target`` veto-UNC + never-fabricate PATTERN) — but with a
different target: a flat ``{ref: {narrative}}`` map (NOT roadmap.yaml nodes), which may not
exist yet (created on first write).

NEVER fabricates: an empty narrative or a non-ATRITO ref raises (the write is strict — distinct
from the read side ``parseAtritoNarrative`` in the Site, which degrades to ``null``).
:func:`list_unnarrated` enumerates ALL ATRITOs from the ledger (no relevance heuristic —
ADR-0038) minus the ones already authored.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml

from journey_core.exceptions import JourneyError
from journey_core.writer import guard_write_target

NARRATIVES_REL = "docs/atrito-narratives.yaml"
LEDGER_REL = "docs/JOURNEY-ATRITOS-FOUNDATION.md"

_REF_RE = re.compile(r"^ATRITO-\d+$")
_LEDGER_HEADER_RE = re.compile(r"^###\s+(ATRITO-\d+)", re.MULTILINE)


def _load_map(path: Path) -> dict[str, Any]:
    """Load the narratives yaml as a dict (``{}`` if absent, empty, or not a mapping)."""
    if not path.is_file():
        return {}
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    return cast("dict[str, Any]", raw) if isinstance(raw, dict) else {}


def _authored_narrative(value: Any) -> str | None:
    """The non-empty narrative string of a yaml entry, or ``None`` (honest degradation)."""
    if not isinstance(value, dict):
        return None
    text = cast("dict[str, Any]", value).get("narrative")
    return text if isinstance(text, str) and text.strip() else None


def set_atrito_narrative(repo_root: str | Path, ref: str, narrative: str) -> Path:
    """Author the didactic ``narrative`` of ATRITO ``ref`` in ``docs/atrito-narratives.yaml``.

    Sets ONLY the given ref, preserving the others; creates the file if absent. NEVER
    fabricates — an empty narrative or a non-``ATRITO-N`` ref raises (the write is strict).
    Writes are routed through the runtime; UNC paths are vetoed (ADR-0004).
    """
    if not _REF_RE.match(ref):
        raise JourneyError(f"set_atrito_narrative: {ref!r} is not an ATRITO ref (ATRITO-N).")
    if not narrative.strip():
        raise JourneyError(
            "set_atrito_narrative refuses an empty narrative (anti-fabrication, ADR-0038)."
        )
    target = guard_write_target(Path(repo_root) / NARRATIVES_REL)
    data = _load_map(target)
    data[ref] = {"narrative": narrative}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target


def list_unnarrated(repo_root: str | Path) -> list[str]:
    """The ATRITOs (from the ledger) still lacking an authored narrative — ALL, no heuristic.

    Enumerates every ``### ATRITO-N`` header in the ledger and subtracts the refs already
    authored (a non-empty ``narrative``) in ``docs/atrito-narratives.yaml``. Returns them in
    ledger order, deduped. Empty ledger or everything-narrated → ``[]``.
    """
    root = Path(repo_root)
    ledger = root / LEDGER_REL
    ledger_text = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    seen: set[str] = set()
    all_refs: list[str] = []
    for m in _LEDGER_HEADER_RE.finditer(ledger_text):
        ref = m.group(1)
        if ref not in seen:
            seen.add(ref)
            all_refs.append(ref)
    authored = {
        ref
        for ref, value in _load_map(root / NARRATIVES_REL).items()
        if _authored_narrative(value) is not None
    }
    return [ref for ref in all_refs if ref not in authored]
