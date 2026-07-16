"""Read/write of the active phase in the HANDOVER ``Fase atual`` Meta row (FR-002/003).

Reading is allowed from any environment; writing is routed through the repository
runtime and UNC paths are vetoed (ADR-0004). The write replaces only the value of the
``Fase atual`` row, preserving the rest of the file.
"""

from __future__ import annotations

import re
from pathlib import Path

from journey_core.exceptions import JourneyError
from journey_core.models.phase_state import PhaseState
from journey_core.writer import guard_write_target

_FASE_ROW = re.compile(
    r"^(?P<prefix>\|\s*\*\*Fase atual\*\*\s*\|\s*)(?P<value>.+?)(?P<suffix>\s*\|)\s*$",
    re.MULTILINE,
)


def read_active_phase(handover_path: str | Path) -> str | None:
    """Return the current ``Fase atual`` value verbatim, or ``None`` if absent."""
    path = Path(handover_path)
    if not path.is_file():
        return None
    match = _FASE_ROW.search(path.read_text(encoding="utf-8"))
    return match.group("value").strip() if match else None


def set_active_phase(handover_path: str | Path, state: PhaseState) -> Path:
    """Write ``state.marker`` into the ``Fase atual`` row, preserving the rest (FR-003).

    Args:
        handover_path: Path to HANDOVER.md.
        state: The phase being opened; ``state.marker`` is the new row value.

    Returns:
        The written path.

    Raises:
        JourneyError: If HANDOVER.md is missing or has no ``Fase atual`` row.
    """
    path = guard_write_target(handover_path)
    if not path.is_file():
        raise JourneyError(f"HANDOVER not found at {path!r}")
    text = path.read_text(encoding="utf-8")
    if not _FASE_ROW.search(text):
        raise JourneyError("HANDOVER has no 'Fase atual' Meta row")
    new = _FASE_ROW.sub(
        lambda m: f"{m.group('prefix')}{state.marker}{m.group('suffix')}", text, count=1
    )
    path.write_text(new, encoding="utf-8")
    return path
