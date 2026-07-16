"""Deterministic write ops for /journey-retrospective (feature 013): numbering + file write.

Mirrors adr_ops (single-source write, anti-drift): next_retro_number reads the on-disk
sequence in docs/retrospectives/ and write_retrospective renders + writes the document,
routing through the repository runtime and vetoing UNC paths (ADR-0004). The directory is TRACKED
(a permanent learning record) and is created on first write.
"""

from __future__ import annotations

import re
from pathlib import Path

from journey_core.models.retrospective import Retrospective
from journey_core.writer import guard_write_target

_RETRO_FILE = re.compile(r"^(?P<num>\d{3})-.+\.md$")


def next_retro_number(retro_dir: str | Path) -> int:
    """Next free 3-digit sequence (first = 1) scanned from docs/retrospectives/."""
    directory = Path(retro_dir)
    if not directory.is_dir():
        return 1
    nums = [
        int(match.group("num"))
        for child in directory.iterdir()
        if (match := _RETRO_FILE.match(child.name)) is not None
    ]
    return (max(nums) + 1) if nums else 1


def write_retrospective(retro_dir: str | Path, retro: Retrospective, number: int) -> Path:
    """Render retro and write <retro_dir>/NNN-slug.md (creates the tracked directory)."""
    target = guard_write_target(Path(retro_dir) / retro.filename(number))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(retro.to_markdown(number), encoding="utf-8")
    return target
