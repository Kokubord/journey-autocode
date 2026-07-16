"""Models for /journey-upgrade (feature 002): tier delta.

Reuses :class:`journey_core.models.project_state.Tier`. The upgrade decision is recorded as a
**regular ADR** (reuse ``adr_ops``/``Adr``) — no parallel model. The methodology-version dimension
(ATRITO-15) and the exact Std→Enterprise delta (ATRITO-50) are **deferred** — not modelled here.
"""

from __future__ import annotations

from pydantic import BaseModel

from journey_core.models.project_state import Tier


class TierDelta(BaseModel):
    """The additive delta between the current tier and the target — what is MISSING (FR-002)."""

    from_tier: Tier
    to_tier: Tier
    missing: list[
        str
    ] = []  # canonical artifact paths absent for the target tier (incl. ``specs/``)
