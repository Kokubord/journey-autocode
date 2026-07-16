"""Parser for HANDOVER.md state detection (supports FR-014)."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

_META_ROW = re.compile(r"^\|\s*\*\*(?P<key>[^*]+)\*\*\s*\|\s*(?P<value>.+?)\s*\|", re.MULTILINE)


class HandoverState(BaseModel):
    """Minimal state extracted from a HANDOVER.md file."""

    exists: bool
    last_update: str | None = None
    current_phase: str | None = None


def parse_handover(path: str | Path) -> HandoverState:
    """Parse a HANDOVER.md file, extracting the meta fields used for detection.

    Args:
        path: Path to the HANDOVER.md file.

    Returns:
        A :class:`HandoverState`; ``exists`` is ``False`` when the file is absent.
    """
    file_path = Path(path)
    if not file_path.is_file():
        return HandoverState(exists=False)
    text = file_path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    for row in _META_ROW.finditer(text):
        meta[row.group("key").strip()] = row.group("value").strip()
    return HandoverState(
        exists=True,
        last_update=meta.get("Última atualização"),
        current_phase=meta.get("Fase atual"),
    )
