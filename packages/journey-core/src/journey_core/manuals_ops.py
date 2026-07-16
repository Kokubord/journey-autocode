"""Shared manual write op (feature 008).

The **single source** the conducting skill reuses to persist a manual (anti-drift, eco do
:mod:`journey_core.adr_ops` / ATRITO-61). The manual **content is authored by the skill**
(judgment) — this only writes it. Writes are routed through the repository runtime and UNC
paths are vetoed (ADR-0004). Manuals document the TARGET project, not Journey (FR-007).
"""

from __future__ import annotations

from pathlib import Path

from journey_core.models.manual import Manual
from journey_core.writer import guard_write_target


def write_manual(repo_root: str | Path, manual: Manual) -> Path:
    """Write a canonical manual to ``docs/manuals/<type>.md`` (FR-001/006); return its path."""
    target = guard_write_target(Path(repo_root) / manual.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(manual.content, encoding="utf-8")
    return target
