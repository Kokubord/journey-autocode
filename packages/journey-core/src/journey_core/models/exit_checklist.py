"""Exit checklist model for /journey-phase-end (feature 007, FR-002).

The checklist blocks the phase closure when a required (blocking) item fails — e.g.
tests failing or CI red (SC-003). "Manuais gerados" is included only at the end of Build
(spec 008); HANDOVER consolidation is tracked but non-blocking.
"""

from __future__ import annotations

from pydantic import BaseModel


class ExitCheckItem(BaseModel):
    """A single exit-checklist item; ``blocking`` items prevent closure when not ``ok``."""

    label: str
    ok: bool
    blocking: bool = True


class ExitChecklist(BaseModel):
    """The phase exit checklist (FR-002)."""

    items: list[ExitCheckItem] = []

    @property
    def blocked(self) -> bool:
        """Whether closure is blocked (any blocking item not ``ok``) — SC-003."""
        return any((not item.ok) and item.blocking for item in self.items)

    @property
    def blocking_failures(self) -> list[str]:
        """Labels of the blocking items that are failing."""
        return [item.label for item in self.items if (not item.ok) and item.blocking]
