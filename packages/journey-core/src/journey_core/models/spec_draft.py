"""Per-feature ``spec.md`` draft handed to /speckit-specify (FR-006, verbete-estreito).

The draft is *delivered* to ``/speckit-specify`` to refine — /journey-discover does
not refine specs (FR-006, SC-005). Drafts live under ``specs/drafts/`` to stay clearly
separate from the speckit-owned ``specs/NNN-feature/`` directories.
"""

from __future__ import annotations

from pydantic import BaseModel


class SpecDraft(BaseModel):
    """A pre-refino ``spec.md`` draft for one identified feature."""

    feature_slug: str
    title: str
    content: str

    @property
    def path(self) -> str:
        """Draft location, clearly separate from speckit-owned ``specs/NNN-*/``."""
        return f"specs/drafts/{self.feature_slug}.spec.md"
