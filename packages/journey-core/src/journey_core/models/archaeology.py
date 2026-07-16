"""Models for /journey-archaeology (feature 003): retroactive ADR proposals.

A proposal **reuses** :class:`journey_core.models.adr.Adr` (``status=Proposto``) — there is no
parallel ADR schema. The archaeology-specific **safety** metadata lives in :class:`RetroProposal`.
Anti-fabrication (FR-007, ATRITO-32): a proposal MUST cite at least one source — *propose, never
assert*; an unsourced proposal is invalid by construction.
"""

from __future__ import annotations

from pydantic import BaseModel, field_validator

from journey_core.models.adr import Adr

#: Canonical retroactivity note (FR-002) — the date is the AUDIT date, not the original decision's.
RETRO_NOTE = "ADR criado retroativamente em {date} após auditoria"


class RetroProposal(BaseModel):
    """A PROPOSED retroactive ADR (an :class:`Adr` with ``status=Proposto``) + safety metadata.

    ``sources`` anchors the proposal in real evidence (git log / specs / PRs) and MUST be non-empty.
    ``uncertain`` flags that the source does not fully support the rationale (FR-007) — the rite
    asks the human to confirm instead of fabricating context.
    """

    adr: Adr
    sources: list[str]
    uncertain: bool = False

    @field_validator("sources")
    @classmethod
    def _sources_non_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError(
                "RetroProposal requires >=1 source (propose-never-assert, FR-007/ATRITO-32)"
            )
        return value
